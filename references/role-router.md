# Role Router and Dynamic Sample Protocol

Route by the business outcome and operating chain, not the job title alone. One JD may contain more than one family; select a primary family, record confidence, and retain secondary modules only when they own material outcomes.

## V1 routes

| Role family | Outcome usually owned | Default sample unit | Required playbook |
| --- | --- | --- | --- |
| Creator/KOL/Affiliate BD | qualified creator supply, usable content, attributed reach or revenue | 10 qualified creators | `creator-partnership-playbook.md` |
| Overseas social/content | audience growth, content performance, community response, profile or lead conversion | 5 direct + 5 mechanism accounts; 10–20 posts | `social-media-playbook.md` |
| Overseas sales/BD | qualified pipeline, meetings, proposals, revenue, expansion | 10 target accounts; 5 buyer roles; 3–5 competitors | `overseas-sales-playbook.md` |
| Ecommerce/Affiliate Growth | listing/store conversion, creator/ad supply, GMV contribution, retention | 10 listings/ads/creator cases; 5 stores | `ecommerce-growth-playbook.md` |

The default sample unit is the role's operating object, not the whole benchmark plan. For company-side roles, add a separate competitor operating-system layer before collecting the unit samples:

```text
comparable brands → campaigns/programs → operating chain → role-specific samples
```

For Creator/KOL roles this normally means brand/campaign benchmarks plus creator samples. Ten creators alone do not satisfy competitive intelligence.

Product marketing, community, localization, tourism, education, and professional-service roles are V2. If one appears, use the generic operating-chain method and mark the route `provisional_v2`; do not imply specialized coverage.

## Routing questions

1. Which business result is the hiring manager likely measured on?
2. What object moves through the workflow: creator, post, account, lead, listing, customer, or community member?
3. Which stage consumes most recurring work?
4. Does the JD combine acquisition, execution, analytics, and operations without clear ownership?
5. Which missing resource would make the stated outcome impossible?

## Sample protocol contract

```yaml
sample_protocol:
  sample_unit: "creator | account | content | prospect | ad | listing | competitor"
  target_count: 10
  inclusion_criteria: []
  exclusion_criteria: []
  required_fields: []
  diversity_dimensions: []
  collected_count: 0
  sufficient: false
  stop_rule: ""
```

Define the protocol before browsing. Choose diversity dimensions that can change the decision: geography, language, scale, audience segment, funnel stage, creator size, business model, or proof mechanism.

## Sufficiency and stop rule

Mark `sufficient: true` only when:

- all included cases meet minimum criteria;
- the set covers material diversity dimensions;
- direct cases and analogous cases are labeled separately;
- new cases repeat known mechanisms;
- the next interview or work-sample decision is stable.

Never lower inclusion criteria to hit ten. Report `6/10 qualified` with the access or market limit and restrict conclusions accordingly.
