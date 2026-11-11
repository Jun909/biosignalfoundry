"""Fixed watchlist for paper-trading batches.

Keep it fixed so batches stay comparable; edit it deliberately and rerun the gate
check (every ticker must resolve through ``core.ticker_gate`` and have prices).
Benchmarks are priced alongside every signal but are never traded.
"""

BENCHMARKS: tuple[str, str] = ("XBI", "IBB")

WATCHLIST: list[str] = [
    # Large-cap commercial
    "AMGN",  # Amgen: large-cap benchmark
    "GILD",  # Gilead Sciences
    "REGN",  # Regeneron
    "VRTX",  # Vertex Pharmaceuticals
    "BIIB",  # Biogen
    # Mid-cap commercial / platform
    "ALNY",  # Alnylam: RNA therapeutics
    "SRPT",  # Sarepta Therapeutics
    "BMRN",  # BioMarin Pharmaceutical
    "IONS",  # Ionis Pharmaceuticals
    "EXEL",  # Exelixis
    "MRNA",  # Moderna
    "HALO",  # Halozyme Therapeutics
    "ACAD",  # ACADIA Pharmaceuticals
    "RARE",  # Ultragenyx
    "PTGX",  # Protagonist Therapeutics
    "NBIX",  # Neurocrine Biosciences
    "UTHR",  # United Therapeutics
    "INCY",  # Incyte
    "JAZZ",  # Jazz Pharmaceuticals
    "INSM",  # Insmed
    # Gene editing
    "CRSP",  # CRISPR Therapeutics
    "BEAM",  # Beam Therapeutics
    "NTLA",  # Intellia Therapeutics
    # Clinical-stage / catalyst-driven
    "VKTX",  # Viking Therapeutics
    "MDGL",  # Madrigal Pharmaceuticals
    "ARWR",  # Arrowhead Pharmaceuticals
    "CYTK",  # Cytokinetics
    "KRYS",  # Krystal Biotech
    "IMVT",  # Immunovant
    "SMMT",  # Summit Therapeutics
]
