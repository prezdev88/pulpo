# Developer Profile Creation Protocol

This document defines how an AI should create a new developer profile for IteraSpec.

## Purpose
Use this protocol when the user wants to create a new developer profile, extend the available staff, or refine a rough developer idea into a reusable profile file under `.iteraspec/developers/`.

## Output Location
- The resulting profile must be written as `.iteraspec/developers/<profile_id>.md`.
- The profile must follow the canonical developer profile format defined in `ITERASPEC.md`.

## Creation Modes
- `Guided Mode`: Ask targeted follow-up questions until the profile can be created with enough specificity.
- `Fast Mode`: If the user already provides enough information, create the profile directly and ask only minimal clarification questions.

## Minimum Required Information
The AI must not finalize a new developer profile unless it can determine all of the following:

- display name
- stable profile ID
- role
- specialty
- seniority
- primary stacks
- architecture style
- preferred work
- preferred testing style
- collaboration style
- whether the profile is lead-eligible
- whether the profile is active
- strengths
- common risks
- when to assign

## Questioning Rule
If any minimum field is missing, vague, or inconsistent, the AI must continue asking targeted questions until the profile is specific enough to be reusable in staffing decisions.

- Prefer short focused questions.
- Ask only what is necessary to reduce ambiguity.
- Do not stop after a name and stack alone.
- Do not create placeholder sections such as `TBD`, `Unknown`, or empty headings in the final profile.

## Suggested Question Areas
When information is incomplete, ask about:

- preferred name for the developer
- technical specialty and strongest stack
- preferred architecture style
- preferred type of work
- preferred testing style
- collaboration style
- strongest qualities
- common tradeoffs or risks
- when the project owner should assign this developer
- whether the developer should be selectable as a lead

## Sufficiency Rule
The AI may stop asking questions and generate the profile only when:

- the profile is specific enough to compare against other developers,
- the project owner could reasonably choose it during staffing,
- and the AI can explain when this developer should be hired instead of another one.

## Consistency Rule
Before finalizing the profile, the AI must verify:

- the profile ID is filesystem-safe and stable,
- the specialty matches the primary stacks,
- the preferred work matches the strengths,
- the common risks are realistic tradeoffs rather than empty praise,
- and the `When To Assign` section is actionable.

## Approval Rule
New developer profiles should be shown to the user for confirmation before they are treated as part of the reusable staff.

## Example Trigger
- "Create a new developer profile"
- "Add a Vue senior specialist"
- "Turn this skill into a developer"
