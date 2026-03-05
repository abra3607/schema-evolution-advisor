from dataclasses import dataclass
from .parser import Operation


@dataclass
class Finding:
    operation: Operation
    risk_level: str  # "safe", "cautious", "dangerous"
    rationale: str
    recommendation: str


def _classify_add_column(op: Operation) -> Finding:
    nullable = op.kwargs.get("nullable", "True")
    has_default = "server_default" in op.kwargs
    col_name = op.args[1] if len(op.args) > 1 else "unknown"

    if nullable == "False" and not has_default:
        return Finding(
            operation=op,
            risk_level="cautious",
            rationale=f"Non-nullable column '{col_name}' without server default will fail on existing rows",
            recommendation="Add server_default or make nullable initially, then backfill",
        )
    return Finding(
        operation=op,
        risk_level="safe",
        rationale=f"Adding nullable column '{col_name}'",
        recommendation="No action needed",
    )


def _classify_drop_column(op: Operation) -> Finding:
    col_name = op.args[1] if len(op.args) > 1 else "unknown"
    return Finding(
        operation=op,
        risk_level="dangerous",
        rationale=f"Dropping column '{col_name}' causes irreversible data loss",
        recommendation="Ensure column data is backed up or migrated before dropping",
    )


def _classify_alter_column(op: Operation) -> Finding:
    col_name = op.args[1] if len(op.args) > 1 else "unknown"
    has_type_change = "type_" in op.kwargs or "existing_type" in op.kwargs
    has_nullable_change = "nullable" in op.kwargs

    if has_type_change:
        return Finding(
            operation=op,
            risk_level="cautious",
            rationale=f"Type change on column '{col_name}' may truncate or lose data",
            recommendation="Verify data compatibility before migrating; consider a two-step migration",
        )
    if has_nullable_change and op.kwargs.get("nullable") == "False":
        return Finding(
            operation=op,
            risk_level="cautious",
            rationale=f"Making column '{col_name}' non-nullable may fail if NULLs exist",
            recommendation="Backfill NULL values before altering",
        )
    return Finding(
        operation=op,
        risk_level="safe",
        rationale=f"Altering column '{col_name}' metadata",
        recommendation="No action needed",
    )


def _classify_create_table(op: Operation) -> Finding:
    table_name = op.args[0] if op.args else "unknown"
    return Finding(
        operation=op,
        risk_level="safe",
        rationale=f"Creating new table '{table_name}'",
        recommendation="No action needed",
    )


def _classify_drop_table(op: Operation) -> Finding:
    table_name = op.args[0] if op.args else "unknown"
    return Finding(
        operation=op,
        risk_level="dangerous",
        rationale=f"Dropping table '{table_name}' causes irreversible data loss",
        recommendation="Ensure all data is backed up or migrated; consider soft-delete first",
    )


def _classify_create_index(op: Operation) -> Finding:
    index_name = op.args[0] if op.args else "unknown"
    return Finding(
        operation=op,
        risk_level="safe",
        rationale=f"Creating index '{index_name}'",
        recommendation="Consider CREATE INDEX CONCURRENTLY for large tables (PostgreSQL)",
    )


def _classify_drop_index(op: Operation) -> Finding:
    index_name = op.args[0] if op.args else "unknown"
    return Finding(
        operation=op,
        risk_level="cautious",
        rationale=f"Dropping index '{index_name}' may degrade query performance",
        recommendation="Verify no critical queries depend on this index",
    )


def _classify_rename_table(op: Operation) -> Finding:
    old_name = op.args[0] if op.args else "unknown"
    new_name = op.args[1] if len(op.args) > 1 else "unknown"
    return Finding(
        operation=op,
        risk_level="cautious",
        rationale=f"Renaming table '{old_name}' to '{new_name}' breaks existing references",
        recommendation="Update all application code and queries referencing the old table name",
    )


_CLASSIFIERS = {
    "add_column": _classify_add_column,
    "drop_column": _classify_drop_column,
    "alter_column": _classify_alter_column,
    "create_table": _classify_create_table,
    "drop_table": _classify_drop_table,
    "create_index": _classify_create_index,
    "drop_index": _classify_drop_index,
    "rename_table": _classify_rename_table,
}


def analyze(operations: list[Operation]) -> list[Finding]:
    findings = []
    for op in operations:
        classifier = _CLASSIFIERS.get(op.op_type)
        if classifier:
            findings.append(classifier(op))
    return findings


def has_dangerous(findings: list[Finding]) -> bool:
    return any(f.risk_level == "dangerous" for f in findings)


def has_cautious_or_dangerous(findings: list[Finding]) -> bool:
    return any(f.risk_level in ("cautious", "dangerous") for f in findings)
