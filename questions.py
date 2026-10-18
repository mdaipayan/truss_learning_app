"""Truss learning app question bank and tutorial content."""

TUTORIALS = [
    {
        "title": "What is a Truss?",
        "content": """A [bold cyan]truss[/bold cyan] is a structural framework composed of straight members
connected at joints (nodes). The members form a series of triangles,
which gives trusses their characteristic strength and rigidity.

Key properties:
  • Members carry only [yellow]axial forces[/yellow] (tension or compression)
  • Loads are applied only at [yellow]joints[/yellow]
  • Joints are assumed to be [yellow]frictionless pins[/yellow]
  • The structure is [yellow]statically determinate[/yellow] when: m + r = 2j
    (m = members, r = reactions, j = joints)

Common uses: bridges, roof structures, transmission towers, cranes.""",
    },
    {
        "title": "Types of Trusses",
        "content": """Common planar truss configurations:

  [bold cyan]Pratt Truss[/bold cyan]
    Vertical members in compression, diagonals in tension.
    Efficient for medium spans. ▲▽▲▽ pattern with verticals.

  [bold cyan]Warren Truss[/bold cyan]
    No vertical members; alternating diagonals form a zig-zag (W shape).
    Diagonals carry both tension and compression depending on position.

  [bold cyan]Howe Truss[/bold cyan]
    Opposite of Pratt: verticals in tension, diagonals in compression.
    Less common in modern design.

  [bold cyan]K-Truss[/bold cyan]
    Diagonals meet a vertical at mid-height, forming a "K" shape.
    Used in very long-span bridges.

  [bold cyan]Fink Truss[/bold cyan]
    V-shaped sub-triangles; common in roof construction.""",
    },
    {
        "title": "Method of Joints",
        "content": """The [bold cyan]Method of Joints[/bold cyan] solves for member forces by analyzing
equilibrium at each joint.

Steps:
  1. Find support reactions using ΣFx=0, ΣFy=0, ΣM=0 for the whole truss.
  2. Start at a joint with [yellow]at most 2 unknown members[/yellow].
  3. Draw a free-body diagram of the joint.
  4. Apply ΣFx = 0 and ΣFy = 0 to solve the two unknowns.
  5. Assume members are in [green]tension[/green] (pulling away from joint).
     A negative result means the member is in [red]compression[/red].
  6. Move to the next joint and repeat.

Tips:
  • Zero-force members can be spotted by inspection:
    - A joint with only 2 non-collinear members and no external load
      → both members are zero-force.
    - A joint with 3 members where 2 are collinear and no load
      → the third member is zero-force.""",
    },
    {
        "title": "Method of Sections",
        "content": """The [bold cyan]Method of Sections[/bold cyan] quickly finds forces in specific members
without analyzing the entire truss joint-by-joint.

Steps:
  1. Find support reactions for the whole truss.
  2. Pass an imaginary [yellow]cutting plane[/yellow] through at most 3 members
     whose forces are unknown.
  3. Consider equilibrium of either half of the cut truss.
  4. Apply ΣFx=0, ΣFy=0, ΣM=0 to solve for the cut member forces.

[bold]Choosing the moment point[/bold]:
  Taking moments about the intersection of two unknown forces eliminates
  those unknowns, letting you solve for the third directly.

When to use it:
  • You only need the force in one or a few specific members.
  • It is much faster than the full method of joints.""",
    },
    {
        "title": "Determinacy and Stability",
        "content": """A truss must be both [bold cyan]statically determinate[/bold cyan] and [bold cyan]stable[/bold cyan].

[bold]The determinacy equation:[/bold]
  m + r = 2j  →  [green]statically determinate[/green]
  m + r < 2j  →  [red]unstable (mechanism)[/red]
  m + r > 2j  →  [yellow]statically indeterminate[/yellow]

  m = number of members
  r = number of external reaction components
  j = number of joints

[bold]Example:[/bold] A simple triangular truss with pin + roller support:
  m = 3, r = 3, j = 3  →  3 + 3 = 2(3) = 6  ✓ Determinate

[bold]Geometric instability[/bold]:
  Even with m + r = 2j, a truss can be unstable if members are
  arranged such that they cannot resist certain load directions.
  Always check geometry, not just the equation.""",
    },
    {
        "title": "Determinacy and Truss Optimization",
        "content": """This topic connects **static determinacy** with the way we optimize a 2D truss.

[bold cyan]1. Count first — then check stability[/bold cyan]
  m = number of members; r = independent support-reaction components;
  j = number of joints.

  m + r = 2j  → determinate by count (if the truss is stable)
  m + r > 2j  → indeterminate by count
  m + r < 2j  → insufficient constraints by count; often a mechanism

The count is a screening rule, not proof of stability. A poor member layout or
incorrect supports can make a truss unstable even when m + r = 2j.

[bold cyan]2. Why determinacy matters in optimization[/bold cyan]
  [green]Determinate truss:[/green]
  For a fixed geometry and external loading, equilibrium determines member forces.
  Changing cross-sectional areas changes stress, stiffness and displacement, but
  does not redistribute the ideal member forces.

  [yellow]Indeterminate truss:[/yellow]
  Equilibrium alone cannot determine every member force. Compatibility of
  deformation and member stiffness (EA/L) are also needed. Changing one member's
  area can redistribute forces to other members.

[bold cyan]3. The optimization problem[/bold cyan]
  Minimize material volume:  V = Σ(Lᵢ Aᵢ)
  subject to limits such as |σᵢ| ≤ σ_allow and δ_max ≤ δ_allow.

  Redundancy can provide alternative load paths and improve stiffness, giving an
  optimizer extra ways to trade member sizes against displacement. But an extra
  member also adds material and constraints: a redundant truss is not
  automatically lighter or more economical.

[bold cyan]4. Try the interactive experiment below[/bold cyan]
Compare a five-member determinate layout with the same layout plus member CD.
The crossed diagonals AD and BC pass one another without a pin joint at their
intersection in this idealized connectivity. The lab shows the determinacy count,
force redistribution as area changes, and the minimum-volume design under
identical axial-stress and displacement limits.

[bold]Important scope note:[/bold] the lab is an educational linear-elastic model.
It does not check member buckling, connections, fabrication, load combinations,
or code compliance. Its sizes are not for direct use in a real structure.""",
    },
    {
        "title": "Determinate Truss: Force, Stress and Displacement",
        "content": """This lesson follows the uploaded study notes on a three-member 3–4–5 plane truss.

[bold cyan]Model and loading[/bold cyan]
A = (0, 0), B = (4, 0) and C = (0, 3) m. Members are AB = 4 m, AC = 3 m and BC = 5 m. A is a pin, B is a vertical roller, and joint C carries Px = 20 kN to the right and Py = 20 kN downward.

[bold cyan]Step 1 — support reactions[/bold cyan]
Taking moments about A gives 4By − (20)(3) = 0, so By = 15 kN. Vertical equilibrium gives Ay = 5 kN. Horizontal equilibrium gives Ax = −20 kN, so the horizontal reaction acts to the left.

[bold cyan]Step 2 — member forces[/bold cyan]
The study notes report AB = 20 kN tension, AC = 5 kN compression and BC = 25 kN compression. A negative member-force result means compression when tension was assumed positive.

[bold cyan]Why area does not change ideal member force[/bold cyan]
For the stated determinate, linearly static problem, equilibrium fixes member forces for prescribed geometry and loading. If A_AB changes from 1000 mm² to 500 mm², N_AB remains 20 kN, but stress rises from 20 MPa to 40 MPa.

Key relationship:
  • Force is determined by equilibrium in this ideal determinate case.
  • Stress is force divided by area.
  • Axial stiffness is EA/L, and displacement depends on NL/(EA).

[bold cyan]Displacement check from the study notes[/bold cyan]
For the stated example, the notes give vertical displacement at C as δ_Cv = 75/A_AC mm when A_AC is in mm². If the allowable vertical displacement is 1 mm, this expression requires A_AC ≥ 75 mm². This is an educational calculation under the stated assumptions, not a complete design check.

[bold]Important qualification[/bold]
The independence of member force from area applies to the usual ideal determinate truss under prescribed static loads. Imposed support movements, thermal strains and nonlinear effects require separate treatment.""",
    },
    {
        "title": "Indeterminate Triangle: Redundant Reaction",
        "content": """This worked example follows the uploaded notes for a three-member truss with one additional support reaction.

[bold cyan]Geometry and supports[/bold cyan]
A = (0, 0), B = (4, 0), C = (0, 3) m. Thus AB = 4 m, AC = 3 m and BC = 5 m. A is a pin; B is a vertical roller; C is a horizontal roller against a vertical guide. Joint C carries Px = 20 kN to the right and Py = 20 kN downward.

[bold cyan]Step 1 — degree of indeterminacy[/bold cyan]
There are m = 3 members, r = 4 reaction components and j = 3 joints. Therefore m + r − 2j = 3 + 4 − 6 = 1. The redundant is the horizontal reaction R = Cx.

[bold cyan]Step 2 — equilibrium in terms of R[/bold cyan]
Assuming member tension is positive, the study notes derive:
  • NAB = 20 + R
  • NAC = 0.75R − 5
  • NBC = −1.25(20 + R)
Equilibrium has reduced the problem to one unknown, but has not yet determined R.

[bold cyan]Step 3 — compatibility at C[/bold cyan]
The horizontal guide prevents horizontal movement, so u_C = 0. Remove R to form the primary determinate structure and apply a unit horizontal load at C. The virtual member forces are nAB = 1, nAC = 0.75 and nBC = −1.25.

The unit-load equation is the sum of N_i n_i L_i/(E A_i) over the three members, set equal to zero. With a common E, the notes obtain:
  R = −[(80000/A1) − (11250/A2) + (156250/A3)] / [(4000/A1) + (1687.5/A2) + (7812.5/A3)]
where A1, A2 and A3 refer to AB, AC and BC respectively, in mm², and R is in kN.

[bold cyan]Numerical cases from the notes[/bold cyan]
Equal areas A1 = A2 = A3 = 1000 mm²: R = −16.667 kN; AB = 3.333 kN tension; AC = 17.500 kN compression; BC = 4.167 kN compression.

Change only A3 to 2000 mm² while A1 = A2 = 1000 mm²: R ≈ −15.309 kN; AB ≈ 4.691 kN tension; AC ≈ 16.482 kN compression; BC ≈ 5.863 kN compression.

[bold]Key insight[/bold]
Changing one member area changes its stiffness EA/L, which changes the compatibility solution and redistributes the member forces. This differs from the ideal determinate example.""",
    },
    {
        "title": "Internal Redundancy: Force Method",
        "content": """This advanced worked example follows the uploaded notes for a rectangular truss with both diagonals.

[bold cyan]Geometry and loading[/bold cyan]
The rectangle has a 4 m span and 3 m height: AB = CD = 4 m, BC = DA = 3 m and AC = BD = 5 m. The supports are A (pin: Ax and Ay) and B (vertical roller: By). A downward load P = 10 kN acts at C.

[bold cyan]Step 1 — count the redundancy[/bold cyan]
There are m = 6 members, r = 3 reactions and j = 4 joints. For a stable truss, Ds = m + r − 2j = 6 + 3 − 8 = 1. The structure is first-degree statically indeterminate. Select diagonal BD as the internal redundant and define X = N_BD.

[bold cyan]Step 2 — form the primary structure[/bold cyan]
Temporarily remove BD. The remaining members are AB, BC, CD, DA and AC. The study notes report the primary forces as NBC⁽⁰⁾ = −10 kN and NAB⁽⁰⁾ = NCD⁽⁰⁾ = NDA⁽⁰⁾ = NAC⁽⁰⁾ = 0. Positive force denotes tension; negative denotes compression.

[bold cyan]Step 3 — apply a unit load in the redundant direction[/bold cyan]
The notes list the virtual member forces nAB = −0.8, nBC = −0.6, nCD = −0.8, nDA = −0.6 and nAC = 1 for the primary structure. The 3–4–5 diagonal has horizontal and vertical direction ratios 4/5 and 3/5.

[bold cyan]Step 4 — compatibility and force recovery[/bold cyan]
For the primary members, the force-method expression uses flexibility terms L_i/(E A_i). The actual member forces are recovered from N_i = N_i⁽⁰⁾ + X n_i. Member areas therefore enter through stiffness and flexibility, and changes in area can alter the redundant force and the resulting force distribution.

[bold]Instructor arithmetic check — verify before grading[/bold]
The uploaded notes report a denominator of 13400/(EA) and X = −1.3433 kN for equal material and equal areas. However, the five displayed primary-member terms using the listed lengths and virtual forces sum to 0.64(4000) + 0.36(3000) + 0.64(4000) + 0.36(3000) + 1²(5000) = 12280, not 13400. The source example also states δ_BD = 0; the compatibility statement should explicitly clarify how relative joint displacement along BD is matched to the deformation of the restored redundant member. Treat the reported numeric result as requiring instructor verification rather than as a verified answer.

[bold cyan]Connection to optimization and glass-box learning[/bold cyan]
Minimum-weight design may minimize W = ρg Σ A_i L_i subject to stress and displacement limits. In an indeterminate truss, N_i depends on the area vector A, so the causal chain is area → stiffness EA/L → compatibility → redundant force → member forces → stress and displacement.

Students should be able to inspect the selected redundant, primary forces, unit-load forces, flexibility terms, compatibility equation, force recovery and the way area changes the response.""",
    },

    {
        "title": "Parallel Bars: Compatibility and Load Sharing",
        "content": """This small model from the uploaded study notes makes the role of compatibility easy to see before solving a full indeterminate truss.

[bold cyan]Model[/bold cyan]
Two axial bars support one rigid plate. Their axial forces are F1 and F2, and the external load is P = 100 kN. The plate remains compatible, so the vertical displacement of both attachment points is equal.

[bold cyan]Step 1 — equilibrium[/bold cyan]
Vertical force balance gives F1 + F2 = P. For P = 100 kN, this is one equation with two unknown member forces. Equilibrium alone cannot tell us how the load is shared.

[bold cyan]Step 2 — compatibility[/bold cyan]
The rigid plate imposes δ1 = δ2. Using δ = FL/(EA), the compatibility equation is F1L1/(E1A1) = F2L2/(E2A2). Rearranging gives F1/F2 = k1/k2, where k = EA/L.

[bold cyan]Step 3 — equal material and equal length[/bold cyan]
If both bars have the same E and L, then F1/F2 = A1/A2. The member with the larger area is stiffer and attracts a larger share of the applied load in this parallel-bar model.

[bold cyan]Numerical load sharing from the notes[/bold cyan]
For P = 100 kN and A1 = 1000 mm²:
  • If A2 = 2000 mm², F1 = 33.33 kN and F2 = 66.67 kN.
  • If A2 = 4000 mm², F1 = 20 kN and F2 = 80 kN.

[bold]Core student insight[/bold]
For the ideal determinate truss, equilibrium generally fixes member forces under prescribed static loading. For a load-sharing system with redundant force paths, equilibrium must be combined with compatibility and stiffness. The parallel-bar model is a simple illustration of why area can affect load distribution in an indeterminate structure.

[bold cyan]Connection to glass-box optimization[/bold cyan]
A learning tool should let students change A1 and A2, inspect the stiffness ratio, see F1 and F2 update, and verify that their sum remains P. That same inspectable causal logic extends to truss optimization: area → stiffness → compatibility/load sharing → member force → stress and displacement.""",
    },

]

QUESTIONS = [
    # Topic: Basics
    {
        "topic": "Basics",
        "question": "Which of the following assumptions is NOT part of the ideal truss model?",
        "options": [
            "Joints are frictionless pins",
            "Members can carry both axial and bending forces",
            "Loads are applied only at joints",
            "Members are straight two-force members",
        ],
        "answer": 1,
        "explanation": "In an ideal truss, members carry only axial forces (tension or compression). "
                       "Bending is neglected — that assumption is what makes them two-force members.",
    },
    {
        "topic": "Basics",
        "question": "For a planar truss to be statically determinate, which equation must hold?",
        "options": [
            "m + r = j",
            "m + r = 2j",
            "m = 2j + r",
            "2m + r = 3j",
        ],
        "answer": 1,
        "explanation": "The determinacy condition for a planar truss is m + r = 2j, where m is the number "
                       "of members, r is the number of external reaction components, and j is the number of joints.",
    },
    {
        "topic": "Basics",
        "question": "A truss with m + r < 2j is classified as:",
        "options": [
            "Statically indeterminate",
            "Statically determinate",
            "Geometrically unstable (mechanism)",
            "Over-constrained",
        ],
        "answer": 2,
        "explanation": "When m + r < 2j, there are fewer equations than unknowns needed to maintain equilibrium, "
                       "meaning the structure cannot resist all possible loads — it is a mechanism (unstable).",
    },
    # Topic: Types
    {
        "topic": "Types of Trusses",
        "question": "In a Pratt truss under a typical downward load, the diagonal members are in:",
        "options": [
            "Compression",
            "Tension",
            "Zero force",
            "Bending",
        ],
        "answer": 1,
        "explanation": "The Pratt truss is designed so that its longer diagonal members carry tension "
                       "(the more efficient loading for slender members), while shorter verticals carry compression.",
    },
    {
        "topic": "Types of Trusses",
        "question": "Which truss type uses a zig-zag of diagonals with NO vertical members?",
        "options": [
            "Pratt truss",
            "Howe truss",
            "Warren truss",
            "Fink truss",
        ],
        "answer": 2,
        "explanation": "The Warren truss has only top chord, bottom chord, and alternating diagonals — "
                       "no vertical members. The equilateral-triangle pattern distributes loads efficiently.",
    },
    # Topic: Method of Joints
    {
        "topic": "Method of Joints",
        "question": "When starting the method of joints, you should begin at a joint with:",
        "options": [
            "The most members connected to it",
            "At most 2 unknown member forces",
            "A known external load applied",
            "3 or more unknown member forces",
        ],
        "answer": 1,
        "explanation": "Each joint provides two equilibrium equations (ΣFx=0, ΣFy=0). To solve, "
                       "you need at most 2 unknowns at the starting joint.",
    },
    {
        "topic": "Method of Joints",
        "question": "You assume all unknown member forces are in tension when applying the method of joints. "
                    "If a member's computed force comes out negative, the member is actually in:",
        "options": [
            "Tension",
            "Zero force",
            "Compression",
            "Shear",
        ],
        "answer": 2,
        "explanation": "A negative value when tension is assumed means the member is actually pushing "
                       "the joint (compression), not pulling it.",
    },
    {
        "topic": "Method of Joints",
        "question": "A joint has exactly 2 members connected to it, no external load, and the two members "
                    "are NOT collinear. Both member forces are:",
        "options": [
            "Equal in magnitude",
            "Both zero-force members",
            "Indeterminate",
            "Both in compression",
        ],
        "answer": 1,
        "explanation": "With no external load and two non-collinear members, equilibrium (ΣFx=0, ΣFy=0) "
                       "can only be satisfied if both forces are zero.",
    },
    # Topic: Method of Sections
    {
        "topic": "Method of Sections",
        "question": "The method of sections works best when you need to find forces in:",
        "options": [
            "All members of the truss simultaneously",
            "Only the support reactions",
            "One or a few specific interior members quickly",
            "Only zero-force members",
        ],
        "answer": 2,
        "explanation": "The method of sections lets you cut through the truss and analyze a free body "
                       "to find specific member forces without solving the entire structure joint by joint.",
    },
    {
        "topic": "Method of Sections",
        "question": "When using the method of sections, the cutting plane should pass through at most:",
        "options": [
            "2 unknown members",
            "3 unknown members",
            "4 unknown members",
            "As many as needed",
        ],
        "answer": 1,
        "explanation": "With 3 equilibrium equations (ΣFx=0, ΣFy=0, ΣM=0) available for the cut section, "
                       "you can only solve for up to 3 unknowns.",
    },
    {
        "topic": "Method of Sections",
        "question": "To directly find one unknown member force using the method of sections, you should "
                    "take moments about the point where:",
        "options": [
            "The largest reaction acts",
            "The two other unknown member forces intersect",
            "The applied load acts",
            "The centroid of the section lies",
        ],
        "answer": 1,
        "explanation": "Taking moments about the intersection of the other two unknown forces eliminates "
                       "those unknowns from the moment equation, leaving only one unknown to solve for.",
    },
    # Topic: Mixed/Applied
    {
        "topic": "Applied",
        "question": "A simply supported truss bridge carries a heavy truck load. Which analysis method "
                    "is fastest for finding the force in a single diagonal member near mid-span?",
        "options": [
            "Method of joints (start from left support)",
            "Method of sections",
            "Finite element analysis",
            "Graphical (Maxwell diagram)",
        ],
        "answer": 1,
        "explanation": "The method of sections lets you cut directly to the member of interest without "
                       "analyzing every joint between the support and that member.",
    },
    {
        "topic": "Applied",
        "question": "A roof truss is carrying snow load (distributed load along the top chord). Before "
                    "applying the method of joints, this load must be:",
        "options": [
            "Ignored, since trusses only carry point loads",
            "Converted to equivalent concentrated loads at the joints",
            "Applied as a uniform pressure on all members",
            "Split equally between all members",
        ],
        "answer": 1,
        "explanation": "The ideal truss assumption requires loads at joints only. Distributed loads are "
                       "converted to statically equivalent concentrated forces at the panel points (joints).",
    },

    # Topic: Determinacy & Optimization
    {
        "topic": "Determinacy & Optimization",
        "question": "For a stable, statically determinate truss, what happens to its ideal member-force distribution when only the member areas change?",
        "options": [
            "The force distribution remains fixed for the same geometry and external loading",
            "Every member force becomes proportional to its area",
            "All member forces become zero",
            "Only the support reactions change with area",
        ],
        "answer": 0,
        "explanation": "In a statically determinate truss, equilibrium determines the forces. Changing areas affects stress, stiffness and displacement, but not the ideal equilibrium force distribution.",
    },
    {
        "topic": "Determinacy & Optimization",
        "question": "In an indeterminate truss, what additional information is needed to determine how forces are shared between members?",
        "options": [
            "Only the number of joints",
            "Compatibility of deformation and member stiffness such as EA/L",
            "Only the density of steel",
            "Only the total truss weight",
        ],
        "answer": 1,
        "explanation": "Redundant member forces depend on equilibrium plus deformation compatibility and relative member stiffness. Changing member areas can therefore redistribute internal forces.",
    },
    {
        "topic": "Determinacy & Optimization",
        "question": "What is the most accurate statement about adding a redundant member during truss optimization?",
        "options": [
            "It always reduces the optimum weight",
            "It always makes every member force smaller",
            "It creates another load path but does not guarantee a lighter optimum",
            "It makes displacement independent of member areas",
        ],
        "answer": 2,
        "explanation": "Redundancy can improve stiffness and permit force redistribution, but the added member also consumes material. The optimum depends on geometry, loads and constraints.",
    },
    {
        "topic": "Determinacy & Optimization",
        "question": "A plane truss has m = 6 members, r = 3 reaction components and j = 4 joints. What does the count m + r − 2j indicate?",
        "options": [
            "One degree of static indeterminacy by count",
            "A determinate truss",
            "An unstable truss by count because the result is positive",
            "Two degrees of static indeterminacy",
        ],
        "answer": 0,
        "explanation": "m + r − 2j = 6 + 3 − 2(4) = 1. Assuming geometric stability and independent supports, this indicates one degree of static indeterminacy by count.",
    },

    {
        "topic": "Determinate vs Indeterminate",
        "question": "For the three-member determinate truss in the study notes, AB carries 20 kN. What happens to its ideal member force if A_AB is reduced from 1000 mm² to 500 mm²?",
        "options": [
            "It remains 20 kN for the same geometry and prescribed loading",
            "It doubles to 40 kN",
            "It falls to 10 kN",
            "It becomes zero",
        ],
        "answer": 0,
        "explanation": "Equilibrium fixes the ideal member force in this determinate example. Reducing area from 1000 to 500 mm² doubles stress from 20 to 40 MPa, but does not change the 20 kN force.",
    },
    {
        "topic": "Indeterminate Triangle",
        "question": "In the uploaded three-member triangle, which quantity is selected as the redundant?",
        "options": [
            "Vertical reaction Ay at A",
            "Vertical reaction By at B",
            "Horizontal reaction R = Cx at C",
            "Member force N_AB",
        ],
        "answer": 2,
        "explanation": "The horizontal guide at C adds a fourth reaction component. For m=3, r=4, j=3, the count is m+r−2j=1, and the notes select R=Cx as the redundant.",
    },
    {
        "topic": "Indeterminate Triangle",
        "question": "For A1=A2=A3=1000 mm² in the uploaded three-member example, what redundant reaction is reported?",
        "options": [
            "R = +16.667 kN",
            "R = −16.667 kN",
            "R = −10.000 kN",
            "R = 0 kN",
        ],
        "answer": 1,
        "explanation": "The compatibility equation in the study notes gives R≈−16.667 kN for equal areas. The negative sign indicates that the actual reaction is opposite the chosen positive horizontal direction.",
    },
    {
        "topic": "Force Method",
        "question": "For the rectangular truss with both diagonals, which member is chosen as the internal redundant in the uploaded notes?",
        "options": [
            "AB",
            "BC",
            "AC",
            "BD",
        ],
        "answer": 3,
        "explanation": "The notes select diagonal BD as X=N_BD and remove it temporarily to form the primary determinate structure.",
    },
    {
        "topic": "Force Method",
        "question": "What should be checked before using the reported redundant force X=−1.3433 kN from the uploaded rectangular-truss notes?",
        "options": [
            "The denominator sum and the compatibility condition",
            "Only the colour of the diagonal",
            "Only the number of plotted nodes",
            "The density of concrete",
        ],
        "answer": 0,
        "explanation": "The listed n²L terms sum to 12,280 mm, not the 13,400 mm reported in the notes. The compatibility statement also needs a clear convention for the restored redundant member, so the numerical result requires instructor verification.",
    },

    {
        "topic": "Compatibility and Load Sharing",
        "question": "Two axial bars with equal E and equal L share P = 100 kN through a rigid plate. If A1 = 1000 mm² and A2 = 2000 mm², what load sharing follows?",
        "options": [
            "F1 = 50 kN, F2 = 50 kN",
            "F1 ≈ 33.33 kN, F2 ≈ 66.67 kN",
            "F1 = 80 kN, F2 = 20 kN",
            "F1 = 100 kN, F2 = 0 kN",
        ],
        "answer": 1,
        "explanation": "Compatibility gives F1/F2 = k1/k2 = A1/A2 = 1/2 for equal material and length. Together with F1+F2=100 kN, this gives F1≈33.33 kN and F2≈66.67 kN.",
    },
]
