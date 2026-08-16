# ProofBound

ProofBound is a GenLayer Intelligent Contract for evidence-based Web3 milestone verification.

It allows a contributor or project to define a milestone with explicit acceptance criteria and submit public evidence such as GitHub repositories, deployed contracts, documentation, or other verifiable URLs.

The contract uses GenLayer's non-deterministic execution and validator consensus to independently evaluate the evidence and determine whether the milestone should be APPROVED or REJECTED.

## Why ProofBound

Many Web3 contribution systems depend on manual review or centralized verification.

ProofBound provides a reusable verification primitive where:

1. A milestone and acceptance criteria are defined.
2. Public evidence is submitted.
3. A leader independently evaluates the evidence.
4. Validators independently evaluate the same evidence.
5. Validators check the substantive decision.
6. Consensus determines the final result.
7. The result is stored on-chain.

This makes the verification process more transparent, reproducible, and suitable for automated Web3 workflows.

## Core Contract

The main implementation is:

`contracts/proofbound.py`

The contract provides:

- Milestone creation
- Explicit acceptance criteria
- Public evidence URL storage
- Evidence retrieval
- LLM-based evidence evaluation
- Independent validator evaluation
- Consensus-based APPROVED or REJECTED result
- Score and explanation storage
- Read-only milestone/result inspection

## Consensus Design

ProofBound uses GenLayer's non-deterministic execution model.

The leader retrieves the submitted public evidence and evaluates it against the milestone criteria.

Validators independently retrieve the same evidence and perform their own evaluation.

The validator function checks the substantive decision field:

`APPROVED`

or

`REJECTED`

If the leader and validator disagree on the substantive status, the consensus validation fails.

The contract only updates its stored milestone result after the consensus-controlled execution returns a result.

## Workflow

```text
Create Milestone
       |
       v
Define Acceptance Criteria
       |
       v
Submit Public Evidence
       |
       v
Leader Evaluation
       |
       v
Independent Validator Evaluation
       |
       v
Consensus Check
       |
       +---- Disagreement ----> Reject Consensus
       |
       v
Final Result
       |
       +---- APPROVED
       |
       +---- REJECTED
