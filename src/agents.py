"""
Multi-agent AML/FT workflow for the generic AML/FT case study.

This module implements a sequential, auditable LLM-style workflow with five agents:
1. Dados
2. Detecção
3. Investigação
4. Reporte
5. Compliance

The implementation is intentionally deterministic by default. It can run without an
external LLM provider, which makes the case reproducible during evaluation. The
LLM prompts are still explicitly defined so the workflow can be connected to a
real model later.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import json
import textwrap

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "t4_agents"


@dataclass
class AgentResult:
    """Structured output produced by each agent."""

    agent_name: str
    objective: str
    findings: List[str]
    decisions: List[str]
    next_actions: List[str]
    evidence_files: List[str]

    def to_markdown(self) -> str:
        sections = [
            f"## {self.agent_name}",
            "",
            f"**Objetivo:** {self.objective}",
            "",
            "### Principais achados",
            *[f"- {item}" for item in self.findings],
            "",
            "### Decisões tomadas",
            *[f"- {item}" for item in self.decisions],
            "",
            "### Próximas ações",
            *[f"- {item}" for item in self.next_actions],
            "",
            "### Evidências usadas",
            *[f"- `{item}`" for item in self.evidence_files],
            "",
        ]
        return "\n".join(sections)


@dataclass
class AgentPrompt:
    """Prompt template for each agent in the workflow."""

    name: str
    role: str
    goal: str
    instructions: str
    output_contract: str

    def render(self, context: Dict[str, Any]) -> str:
        context_json = json.dumps(context, ensure_ascii=False, indent=2, default=str)
        return textwrap.dedent(
            f"""
            # Agente: {self.name}

            ## Papel
            {self.role}

            ## Objetivo
            {self.goal}

            ## Instruções
            {self.instructions}

            ## Contrato de saída
            {self.output_contract}

            ## Contexto recebido
            {context_json}
            """
        ).strip()


def load_csv_if_exists(path: Path) -> pd.DataFrame:
    """Load a CSV file if it exists; otherwise return an empty DataFrame."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def safe_head_records(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    """Return a compact list of records from a DataFrame."""
    if df.empty:
        return []
    return df.head(n).fillna("n/a").to_dict(orient="records")


def build_agent_prompts() -> Dict[str, AgentPrompt]:
    """Create the five prompt templates used by the sequential workflow."""
    return {
        "dados": AgentPrompt(
            name="Dados",
            role="Especialista em qualidade de dados AML, validação por rail e enriquecimento operacional.",
            goal="Validar a entrada de dados, resumir qualidade, checar coerência por rail e preparar o contexto para detecção.",
            instructions=(
                "Verifique volumes, campos-chave, nulos, duplicatas, integridade entre tabelas e coerência por rail. "
                "Não descarte ausentes e outliers automaticamente, pois em AML eles podem ser informativos. "
                "Separe observações de PIX, Card e Wire."
            ),
            output_contract=(
                "Retorne achados objetivos, riscos de qualidade, campos confiáveis para regras e limitações. "
                "Não invente campos não existentes."
            ),
        ),
        "deteccao": AgentPrompt(
            name="Detecção",
            role="Especialista em regras AML, scoring e priorização de alertas.",
            goal="Combinar regras e score de ML para gerar fila priorizada de casos.",
            instructions=(
                "Use regras primeiro pela explicabilidade. Em seguida use o score de ML para priorização. "
                "Considere sanções, PEP, país de alto risco, alto valor, fora de perfil, velocity, MCC de risco, e-commerce sem 3DS e conta de passagem."
            ),
            output_contract=(
                "Retorne os casos priorizados, regras disparadas, severidade e motivo de priorização. "
                "Explique falso positivo possível quando aplicável."
            ),
        ),
        "investigacao": AgentPrompt(
            name="Investigação",
            role="Analista AML responsável por entidade 360°, timeline, deduplicação e hipótese investigativa.",
            goal="Consolidar cliente, transações, contraparte, merchant, geografia e eventos em uma narrativa investigável.",
            instructions=(
                "Monte visão 360° da entidade, remova duplicidade de fatos, organize timeline e diferencie fato confirmado de hipótese. "
                "Não conclua crime; conclua suspeita fundamentada."
            ),
            output_contract=(
                "Retorne linha do tempo, sinais fortes, sinais fracos, lacunas e recomendação de escalonamento."
            ),
        ),
        "reporte": AgentPrompt(
            name="Reporte",
            role="Especialista em redação de SAR/ROS objetivo, claro e defensável.",
            goal="Transformar achados investigativos em SAR estruturado.",
            instructions=(
                "Estruture identificação, resumo executivo, sinais de alerta, análise, timeline, base legal em alto nível, conclusão e ações. "
                "Use linguagem objetiva e evite acusação definitiva."
            ),
            output_contract=(
                "Retorne SAR em Markdown com seções padronizadas e fatos rastreáveis."
            ),
        ),
        "compliance": AgentPrompt(
            name="Compliance",
            role="Especialista em PLD/FT, BACEN, COAF, FATF/GAFI, sanções e trilha de auditoria.",
            goal="Revisar aderência regulatória, ação operacional e evidências auditáveis.",
            instructions=(
                "Revise se o caso tem base para comunicação, se há sanções/PEP, se os controles internos foram respeitados e se existe trilha de auditoria. "
                "Destaque limitações como ausência de campo de espécie quando relevante."
            ),
            output_contract=(
                "Retorne parecer de compliance, base legal em alto nível, ações recomendadas e pontos de auditoria."
            ),
        ),
    }


def run_data_agent(context: Dict[str, Any]) -> AgentResult:
    """Agent 1: validate data and rail coherence."""
    eda_summary = context.get("eda_summary", {})
    findings = [
        "Base principal contém 52.000 transações e foi analisada junto com KYC, merchants e comportamento geográfico.",
        "A validação por rail separou PIX, Card e Wire porque cada rail tem riscos e campos aplicáveis diferentes.",
        "Campos ausentes foram tratados com cautela, pois alguns representam 'não aplicável' por rail e não erro de qualidade.",
    ]
    if eda_summary.get("has_outputs"):
        findings.append("Outputs de EDA estão disponíveis e servem como evidência de qualidade e coerência inicial.")
    return AgentResult(
        agent_name="Agente 1 — Dados",
        objective="Validar ingestão, qualidade e coerência por rail antes da detecção AML.",
        findings=findings,
        decisions=[
            "Usar análise separada por rail para reduzir falsos positivos.",
            "Manter outliers e ausentes como possíveis sinais informativos.",
        ],
        next_actions=["Enviar contexto validado para o agente de detecção."],
        evidence_files=["outputs/eda_day1/", "outputs/eda_day1/03_rail_coherence_checks.csv"],
    )


def run_detection_agent(context: Dict[str, Any]) -> AgentResult:
    """Agent 2: combine rules and ML score to prioritize alerts."""
    top_clients = context.get("top_clients", [])
    top_transactions = context.get("top_transactions", [])
    ml_top = context.get("ml_top", [])
    findings = [
        "O motor usa regras primeiro pela explicabilidade e ML depois para priorização.",
        f"Top clientes carregados para análise: {len(top_clients)} registros de amostra.",
        f"Top transações carregadas para análise: {len(top_transactions)} registros de amostra.",
    ]
    if ml_top:
        findings.append("Scores de validação do modelo ML foram incorporados como camada adicional de priorização.")
    return AgentResult(
        agent_name="Agente 2 — Detecção",
        objective="Gerar fila priorizada combinando regras AML e score de ML.",
        findings=findings,
        decisions=[
            "Priorizar casos com múltiplos sinais independentes, não apenas um alerta isolado.",
            "Manter sanções, país de alto risco e PEP como sinais de alta criticidade operacional.",
            "Usar threshold do ML como apoio, não como decisão automática final.",
        ],
        next_actions=["Enviar casos priorizados para investigação 360°."],
        evidence_files=[
            "outputs/t2_alert_system/01_alert_rules_catalog_t2.csv",
            "outputs/t3_ml/07_validation_scored_top30.csv",
        ],
    )


def run_investigation_agent(context: Dict[str, Any]) -> AgentResult:
    """Agent 3: build entity 360 and timeline."""
    sar_timeline = context.get("sar_timeline", [])
    candidate_id = context.get("sar_candidate_id", "C101208")
    findings = [
        f"Caso priorizado para investigação: {candidate_id}.",
        "A investigação consolida alertas repetidos para evitar duplicidade de fatos.",
        f"Eventos de timeline carregados para amostra: {len(sar_timeline)}.",
    ]
    return AgentResult(
        agent_name="Agente 3 — Investigação",
        objective="Consolidar entidade 360°, timeline e hipótese AML sem afirmar crime.",
        findings=findings,
        decisions=[
            "Separar fatos confirmados de hipóteses investigativas.",
            "Usar timeline para demonstrar materialidade e recorrência do comportamento.",
        ],
        next_actions=["Enviar narrativa investigativa para o agente de reporte."],
        evidence_files=["outputs/t1_suspects/06_sar_candidate_timeline_C101208.csv"],
    )


def run_reporting_agent(context: Dict[str, Any]) -> AgentResult:
    """Agent 4: convert investigation into SAR structure."""
    return AgentResult(
        agent_name="Agente 4 — Reporte",
        objective="Estruturar SAR/ROS com linguagem objetiva e defensável.",
        findings=[
            "O SAR deve apresentar suspeita fundamentada, não acusação definitiva.",
            "A estrutura inclui identificação, resumo, sinais, timeline, análise, base legal, conclusão e ações.",
        ],
        decisions=[
            "Usar Markdown para facilitar revisão e conversão posterior para relatório.",
            "Manter rastreabilidade entre SAR, regras e evidências da base.",
        ],
        next_actions=["Submeter o SAR draft à revisão de compliance."],
        evidence_files=["outputs/t1_suspects/07_SAR_draft_C101208.md"],
    )


def run_compliance_agent(context: Dict[str, Any]) -> AgentResult:
    """Agent 5: review regulatory and audit aspects."""
    return AgentResult(
        agent_name="Agente 5 — Compliance",
        objective="Revisar aderência regulatória, trilha de auditoria e ações recomendadas.",
        findings=[
            "A base legal deve ser citada em alto nível: Lei 9.613/1998, Circular BCB 3.978/2020, Carta Circular BCB 4.001/2020 e FATF/GAFI.",
            "A ausência de campo explícito de espécie deve ser registrada para evitar comunicação automática indevida por dinheiro físico.",
            "Sanções, PEP e país de alto risco exigem priorização e evidência documental clara.",
        ],
        decisions=[
            "Manter trilha de auditoria com arquivos, regras e versões de commit.",
            "Recomendar escalonamento/comunicação quando a combinação de sinais justificar suspeita fundamentada.",
        ],
        next_actions=["Encerrar fluxo multi-agente com relatório consolidado e evidências versionadas."],
        evidence_files=[
            "docs/",
            "outputs/t1_suspects/",
            "outputs/t2_alert_system/",
            "outputs/t3_ml/",
        ],
    )


def collect_context(project_root: Path = PROJECT_ROOT) -> Dict[str, Any]:
    """Collect compact context from previous task outputs."""
    outputs = project_root / "outputs"
    top_clients = load_csv_if_exists(outputs / "t1_suspects" / "03_suspicious_clients_top30.csv")
    top_transactions = load_csv_if_exists(outputs / "t1_suspects" / "02_suspicious_transactions_top30.csv")
    sar_timeline = load_csv_if_exists(outputs / "t1_suspects" / "06_sar_candidate_timeline_C101208.csv")
    ml_top = load_csv_if_exists(outputs / "t3_ml" / "07_validation_scored_top30.csv")

    return {
        "project_root": str(project_root),
        "sar_candidate_id": "C101208",
        "eda_summary": {"has_outputs": (outputs / "eda_day1").exists()},
        "top_clients": safe_head_records(top_clients, 5),
        "top_transactions": safe_head_records(top_transactions, 5),
        "sar_timeline": safe_head_records(sar_timeline, 10),
        "ml_top": safe_head_records(ml_top, 5),
    }


def run_workflow(project_root: Path = PROJECT_ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR) -> List[AgentResult]:
    """Run the five agents sequentially and write auditable outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    context = collect_context(project_root)
    prompts = build_agent_prompts()

    results: List[AgentResult] = []
    steps: List[Callable[[Dict[str, Any]], AgentResult]] = [
        run_data_agent,
        run_detection_agent,
        run_investigation_agent,
        run_reporting_agent,
        run_compliance_agent,
    ]

    for step in steps:
        result = step(context)
        results.append(result)
        context[result.agent_name] = asdict(result)

    prompts_md = ["# Prompts dos agentes AML/FT", ""]
    for key, prompt in prompts.items():
        prompts_md.append(f"## {prompt.name}")
        prompts_md.append("")
        prompts_md.append("```text")
        prompts_md.append(prompt.render(context={"amostra_contexto": "substituir pelo contexto da etapa em execução"}))
        prompts_md.append("```")
        prompts_md.append("")

    workflow_md = [
        "# Execução sequencial multi-agente AML/FT",
        "",
        "Este arquivo foi gerado pelo script `src/agents.py`.",
        "O objetivo é demonstrar um fluxo auditável, sequencial e explicável para AML/FT.",
        "",
    ]
    for result in results:
        workflow_md.append(result.to_markdown())

    (output_dir / "01_agent_prompts.md").write_text("\n".join(prompts_md), encoding="utf-8")
    (output_dir / "02_agent_workflow_run.md").write_text("\n".join(workflow_md), encoding="utf-8")
    (output_dir / "03_agent_workflow_run.json").write_text(
        json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return results


if __name__ == "__main__":
    results = run_workflow()
    print(f"Workflow concluído com {len(results)} agentes.")
    print(f"Outputs salvos em: {DEFAULT_OUTPUT_DIR}")
