# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing


class ProofBound(gl.Contract):
    """
    ProofBound is an evidence-based Web3 milestone adjudicator.

    A contributor submits public evidence for a milestone.
    The leader evaluates the evidence against explicit criteria.
    Validators independently repeat the evaluation and verify
    the substantive decision before consensus is accepted.
    """

    milestone_title: str
    milestone_criteria: str
    evidence_url: str
    status: str
    score: int
    decision: str
    analysis: str

    def __init__(self):
        self.milestone_title = ""
        self.milestone_criteria = ""
        self.evidence_url = ""
        self.status = "UNINITIALIZED"
        self.score = 0
        self.decision = ""
        self.analysis = ""

    @gl.public.write
    def create_milestone(
        self,
        title: str,
        criteria: str,
        evidence_url: str,
    ) -> None:
        self.milestone_title = title
        self.milestone_criteria = criteria
        self.evidence_url = evidence_url
        self.status = "PENDING"
        self.score = 0
        self.decision = ""
        self.analysis = ""

    @gl.public.write
    def evaluate_milestone(self) -> typing.Any:
        if not self.evidence_url:
            raise gl.UserError("No evidence URL configured")

        title = self.milestone_title
        criteria = self.milestone_criteria
        evidence_url = self.evidence_url

        def leader_fn():
            response = gl.nondet.web.get(evidence_url)
            evidence = response.body.decode("utf-8")

            prompt = f"""
You are evaluating a Web3 contribution milestone.

Milestone:
{title}

Acceptance criteria:
{criteria}

Public evidence:
{evidence}

Determine whether the evidence satisfies the acceptance criteria.

Return JSON with exactly these fields:
{{
  "status": "APPROVED" or "REJECTED",
  "score": integer from 0 to 100,
  "decision": "short decision",
  "analysis": "brief evidence-grounded explanation"
}}

Rules:
- Approve only when the evidence materially satisfies the criteria.
- Reject missing, irrelevant, contradictory, or insufficient evidence.
- Never invent facts or work not supported by the evidence.
- The score must reflect the evidence against the criteria.
"""

            return gl.nondet.exec_prompt(
                prompt,
                response_format="json",
            )

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False

            response = gl.nondet.web.get(evidence_url)
            evidence = response.body.decode("utf-8")

            prompt = f"""
Independently evaluate this Web3 milestone.

Milestone:
{title}

Acceptance criteria:
{criteria}

Public evidence:
{evidence}

Return JSON with exactly these fields:
{{
  "status": "APPROVED" or "REJECTED",
  "score": integer from 0 to 100,
  "decision": "short decision",
  "analysis": "brief explanation"
}}

Do not trust the proposed result.
Independently determine whether the evidence satisfies the criteria.
The status is the critical consensus field.
Scores may differ slightly between independent evaluations.
"""

            validator_result = gl.nondet.exec_prompt(
                prompt,
                response_format="json",
            )

            leader_status = leader_result.calldata["status"]
            validator_status = validator_result["status"]

            if leader_status not in ["APPROVED", "REJECTED"]:
                return False

            if validator_status not in ["APPROVED", "REJECTED"]:
                return False

            return leader_status == validator_status

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn,
        )

        self.status = result["status"]
        self.score = result["score"]
        self.decision = result["decision"]
        self.analysis = result["analysis"]

        return result

    @gl.public.view
    def get_milestone(self) -> typing.Any:
        return {
            "title": self.milestone_title,
            "criteria": self.milestone_criteria,
            "evidence_url": self.evidence_url,
            "status": self.status,
            "score": self.score,
            "decision": self.decision,
            "analysis": self.analysis,
        }
