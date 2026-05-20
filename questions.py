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
]
