from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import csv
import json
import math
from enum import Enum
from collections import defaultdict


class MeasureType(Enum):
    AGNOSTIC = "agnostic"
    LINEAR = "linear"
    LOG_UNIFORM = "log_uniform"
    JEFFREYS = "jeffreys"


class DependencyModel(Enum):
    A = "6_independent"
    B = "4_effective_dof"
    C = "propagated"


CONSTANT_PRIOR_RANGES = {
    "alpha": {"linear": [0.0, 1.0], "log": [-10.0, 0.0]},
    "alpha_s": {"linear": [0.0, 1.0], "log": [-10.0, 0.0]},
    "mu_e_over_m_p": {"linear": [0.0, 0.42], "log": [-4.0, -0.38]},
    "alpha_G": {"linear": [0.0, 1.0], "log": [-45.0, 0.0]},
    "vev_over_Mpl": {"linear": [0.0, 1.0], "log": [-20.0, 0.0]},
    "cosmological_constant": {"linear": [0.0, 1.0], "log": [-124.0, 0.0]},
}

CONSTANT_OBSERVED_VALUES = {
    "alpha": 0.007297,
    "alpha_s": 0.1179,
    "mu_e_over_m_p": 0.0005446,
    "alpha_G": 5.9e-39,
    "vev_over_Mpl": 2e-17,
    "cosmological_constant": 2e-122,
}

TIER_DESCRIPTIONS = {
    1: "stable chemistry",
    2: "long-lived stars",
    3: "complex chemistry (carbon)",
    4: "information processing",
}

CONSTANT_NAMES = {
    "alpha": "α",
    "alpha_s": "αₛ",
    "mu_e_over_m_p": "μ",
    "alpha_G": "α_G",
    "vev_over_Mpl": "v/M_Pl",
    "cosmological_constant": "Λ",
}

DEPENDENCY_GROUPS = {
    "group_1": {
        "members": ["alpha"],
        "effective_parameter": "alpha",
        "description": "isolated — no known dependencies",
    },
    "group_2": {
        "members": ["alpha_s", "mu_e_over_m_p", "alpha_G"],
        "effective_parameter": "alpha_s",
        "description": "coupled — αₛ drives m_p → μ and α_G",
    },
    "group_3": {
        "members": ["vev_over_Mpl"],
        "effective_parameter": "vev_over_Mpl",
        "description": "weakly coupled to αₛ and Λ",
    },
    "group_4": {
        "members": ["cosmological_constant"],
        "effective_parameter": "cosmological_constant",
        "description": "nearly isolated — weak link to v/M_Pl",
    },
}


@dataclass
class Bound:
    source_id: str
    citation: str
    constant: str
    bound_type: str
    bound_low: Optional[float]
    bound_high: Optional[float]
    observed_value: float
    bound_as_fraction: str
    life_criterion: str
    tier: int
    variation: str
    methodology: str
    confidence: str
    contested_by: str
    notes: str

    @property
    def has_numerical_lower(self) -> bool:
        if self.bound_low is None:
            return False
        if self.bound_type == "no_bound":
            return False
        return True

    @property
    def has_numerical_upper(self) -> bool:
        if self.bound_high is None:
            return False
        if self.bound_type == "no_bound":
            return False
        return True

    @property
    def log_range_decades(self) -> Optional[float]:
        if not self.has_numerical_lower or not self.has_numerical_upper:
            return None
        return math.log10(self.bound_high) - math.log10(self.bound_low)

    @property
    def linear_range(self) -> Optional[float]:
        if not self.has_numerical_lower or not self.has_numerical_upper:
            return None
        return self.bound_high - self.bound_low

    def provenance(self) -> str:
        return f"{self.source_id}|{self.citation}|{self.constant}|T{self.tier}|{self.methodology}"


class BoundDatabase:
    _instance = None

    def __init__(self, csv_path: str = None):
        self.bounds: List[Bound] = []
        self._by_constant: Dict[str, List[Bound]] = defaultdict(list)
        self._by_tier: Dict[int, List[Bound]] = defaultdict(list)
        self._by_constant_and_tier: Dict[Tuple[str, int], List[Bound]] = defaultdict(list)
        if csv_path:
            self.load(csv_path)
            BoundDatabase._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

    def load(self, path: str):
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bound = self._parse_row(row)
                if bound is None:
                    continue
                self.bounds.append(bound)
                self._by_constant[bound.constant].append(bound)
                self._by_tier[bound.tier].append(bound)
                self._by_constant_and_tier[(bound.constant, bound.tier)].append(bound)

    def _parse_row(self, row: dict) -> Optional[Bound]:
        constant = row["constant"].strip()
        bound_type = row["bound_type"].strip()
        if constant == "general" or constant == "":
            return None
        abs_bound = constant in ("initial_conditions", "entropy", "carbon_resonance", "alpha_AND_alpha_s", "charge_and_mass")
        if abs_bound:
            return None

        bound_low = self._parse_float(row.get("bound_low", ""), None)
        bound_high = self._parse_float(row.get("bound_high", ""), None)

        if constant in CONSTANT_OBSERVED_VALUES:
            observed = CONSTANT_OBSERVED_VALUES[constant]
        else:
            try:
                observed = float(row["observed_value"])
            except (ValueError, KeyError):
                observed = 0.0

        try:
            tier = int(row.get("tier", 0))
        except (ValueError, TypeError):
            tier = 0

        return Bound(
            source_id=row.get("source_id", ""),
            citation=row.get("citation", ""),
            constant=constant,
            bound_type=bound_type,
            bound_low=bound_low,
            bound_high=bound_high,
            observed_value=observed,
            bound_as_fraction=row.get("bound_as_fraction", ""),
            life_criterion=row.get("life_criterion", ""),
            tier=tier,
            variation=row.get("variation", ""),
            methodology=row.get("methodology", ""),
            confidence=row.get("confidence", ""),
            contested_by=row.get("contested_by", ""),
            notes=row.get("notes", ""),
        )

    def _parse_float(self, val: str, default: float = None) -> Optional[float]:
        val = val.strip()
        if val == "" or val == "-" or val == "none" or val == "NA":
            return default
        try:
            return float(val)
        except ValueError:
            return default

    def bounds_for_constant(self, constant: str) -> List[Bound]:
        return self._by_constant.get(constant, [])

    def bounds_for_tier(self, tier: int) -> List[Bound]:
        return self._by_tier.get(tier, [])

    def bounds_for(self, constant: str, tier: int) -> List[Bound]:
        return self._by_constant_and_tier.get((constant, tier), [])

    def all_constants(self) -> List[str]:
        return [c for c in CONSTANT_OBSERVED_VALUES.keys() if c in self._by_constant]

    def tiers_present(self) -> List[int]:
        return sorted(self._by_tier.keys())


@dataclass
class ProbabilityResult:
    constant: str
    tier: int
    measure: MeasureType
    bound_low: float
    bound_high: float
    prior_low: float
    prior_high: float
    probability: float
    probability_label: str
    provenance: List[str]
    is_measure_dominated: bool
    is_blocked: bool
    block_reason: str = ""


class MeasureEngine:
    PATHOLOGICAL_LOG_LINEAR = {"alpha_G", "vev_over_Mpl", "cosmological_constant"}

    def __init__(self, database: BoundDatabase):
        self.db = database

    def compute(self, bound: Bound, measure: MeasureType) -> ProbabilityResult:
        if measure == MeasureType.AGNOSTIC:
            return self._agnostic(bound)
        elif measure == MeasureType.LOG_UNIFORM:
            return self._log_uniform(bound)
        elif measure == MeasureType.LINEAR:
            return self._linear(bound)
        elif measure == MeasureType.JEFFREYS:
            return self._jeffreys(bound)
        else:
            raise ValueError(f"Unknown measure: {measure}")

    def _agnostic(self, bound: Bound) -> ProbabilityResult:
        return ProbabilityResult(
            constant=bound.constant,
            tier=bound.tier,
            measure=MeasureType.AGNOSTIC,
            bound_low=bound.bound_low if bound.has_numerical_lower else float("nan"),
            bound_high=bound.bound_high if bound.has_numerical_upper else float("nan"),
            prior_low=float("nan"),
            prior_high=float("nan"),
            probability=float("nan"),
            probability_label="Cannot assign probability — no well-defined measure",
            provenance=[bound.provenance()],
            is_measure_dominated=False,
            is_blocked=False,
        )

    def _get_prior_range(self, constant: str, measure_type: str) -> Tuple[float, float]:
        if constant in CONSTANT_PRIOR_RANGES:
            pr = CONSTANT_PRIOR_RANGES[constant]
            if measure_type in pr:
                return tuple(pr[measure_type])
        return (float("nan"), float("nan"))

    def _log_uniform(self, bound: Bound) -> ProbabilityResult:
        if not bound.has_numerical_lower or not bound.has_numerical_upper:
            return self._blocked(bound, MeasureType.LOG_UNIFORM, "Bound not numerical")

        prior_low, prior_high = self._get_prior_range(bound.constant, "log")
        if math.isnan(prior_low) or math.isnan(prior_high):
            return self._blocked(bound, MeasureType.LOG_UNIFORM, "No prior range defined")

        total_decades = prior_high - prior_low
        life_decades = math.log10(bound.bound_high) - math.log10(bound.bound_low)

        probability = life_decades / total_decades

        return ProbabilityResult(
            constant=bound.constant,
            tier=bound.tier,
            measure=MeasureType.LOG_UNIFORM,
            bound_low=bound.bound_low,
            bound_high=bound.bound_high,
            prior_low=10 ** prior_low,
            prior_high=10 ** prior_high,
            probability=probability,
            probability_label=f"{life_decades:.4f} / {total_decades:.0f} decades = {probability:.2e}",
            provenance=[bound.provenance()],
            is_measure_dominated=False,
            is_blocked=False,
        )

    def _linear(self, bound: Bound) -> ProbabilityResult:
        if not bound.has_numerical_lower or not bound.has_numerical_upper:
            return self._blocked(bound, MeasureType.LINEAR, "Bound not numerical")

        prior_low, prior_high = self._get_prior_range(bound.constant, "linear")
        if math.isnan(prior_low) or math.isnan(prior_high):
            return self._blocked(bound, MeasureType.LINEAR, "No prior range defined")

        total_range = prior_high - prior_low
        life_range = bound.bound_high - bound.bound_low
        probability = life_range / total_range

        is_dominated = bound.constant in self.PATHOLOGICAL_LOG_LINEAR

        return ProbabilityResult(
            constant=bound.constant,
            tier=bound.tier,
            measure=MeasureType.LINEAR,
            bound_low=bound.bound_low,
            bound_high=bound.bound_high,
            prior_low=prior_low,
            prior_high=prior_high,
            probability=probability,
            probability_label=f"({life_range:.2e}) / ({total_range:.0f}) = {probability:.2e}",
            provenance=[bound.provenance()],
            is_measure_dominated=is_dominated,
            is_blocked=False,
        )

    def _jeffreys(self, bound: Bound) -> ProbabilityResult:
        return self._log_uniform(bound)

    def _blocked(self, bound: Bound, measure: MeasureType, reason: str) -> ProbabilityResult:
        return ProbabilityResult(
            constant=bound.constant,
            tier=bound.tier,
            measure=measure,
            bound_low=float("nan"),
            bound_high=float("nan"),
            prior_low=float("nan"),
            prior_high=float("nan"),
            probability=float("nan"),
            probability_label=f"BLOCKED: {reason}",
            provenance=[bound.provenance()],
            is_measure_dominated=False,
            is_blocked=True,
            block_reason=reason,
        )


@dataclass
class DependencyResult:
    model: DependencyModel
    tier: int
    measure: MeasureType
    groups: Dict[str, ProbabilityResult]
    joint_probability: float
    joint_label: str
    is_blocked: bool
    block_reason: str
    provenance: List[str]


class DependencyEngine:
    def __init__(self, database: BoundDatabase, measure_engine: MeasureEngine):
        self.db = database
        self.me = measure_engine

    def compute(self, model: DependencyModel, tier: int, measure: MeasureType) -> DependencyResult:
        if model == DependencyModel.A:
            return self._model_a(tier, measure)
        elif model == DependencyModel.B:
            return self._model_b(tier, measure)
        elif model == DependencyModel.C:
            return self._model_c(tier, measure)
        else:
            raise ValueError(f"Unknown model: {model}")

    def _best_bound(self, constant: str, tier: int, measure: MeasureType) -> Optional[ProbabilityResult]:
        bounds = self.db.bounds_for(constant, tier)
        if not bounds:
            return None

        best_bound = None
        best_prob = float("inf")

        for b in bounds:
            if b.contested_by and "refuted" in b.contested_by.lower():
                continue
            if b.confidence.lower() == "low":
                continue

            result = self.me.compute(b, measure)
            if result.is_blocked:
                continue

            if result.probability < best_prob:
                best_prob = result.probability
                best_bound = result

        return best_bound

    def _tier_relevant_constants(self, tier: int) -> List[str]:
        if tier == 1:
            return ["alpha", "alpha_s", "vev_over_Mpl"]
        elif tier == 2:
            return ["alpha", "alpha_s", "mu_e_over_m_p", "alpha_G", "vev_over_Mpl", "cosmological_constant"]
        elif tier >= 3:
            return ["alpha", "alpha_s", "mu_e_over_m_p", "alpha_G", "vev_over_Mpl", "cosmological_constant"]
        else:
            return []

    def _model_a(self, tier: int, measure: MeasureType) -> DependencyResult:
        relevant = self._tier_relevant_constants(tier)
        group_results = {}
        provenance = []
        joint_prob = 1.0
        is_blocked = False
        blocked_by = ""

        for constant in relevant:
            bounds = self.db.bounds_for(constant, tier)
            if not bounds:
                if constant == "mu_e_over_m_p":
                    group_results[constant] = ProbabilityResult(
                        constant=constant, tier=tier, measure=measure,
                        bound_low=float("nan"), bound_high=float("nan"),
                        prior_low=float("nan"), prior_high=float("nan"),
                        probability=float("nan"),
                        probability_label="UNBOUNDED: μ has no published Tier-3 bound",
                        provenance=[], is_measure_dominated=False,
                        is_blocked=False,
                    )
                    continue
                alternate_tiers = [t for t in self.db.tiers_present() if t >= tier]
                for at in alternate_tiers:
                    bounds = self.db.bounds_for(constant, at)
                    if bounds:
                        break

            best = self._best_bound(constant, tier if bounds else max(1, tier-1), measure)
            if best is None:
                group_results[constant] = ProbabilityResult(
                    constant=constant, tier=tier, measure=measure,
                    bound_low=float("nan"), bound_high=float("nan"),
                    prior_low=float("nan"), prior_high=float("nan"),
                    probability=float("nan"),
                    probability_label="NO_BOUND",
                    provenance=[], is_measure_dominated=False,
                    is_blocked=True, block_reason="No bound found",
                )
                is_blocked = True
                blocked_by = f"No bound for {constant}"
                continue

            group_results[constant] = best
            provenance.extend(best.provenance)
            if not best.is_blocked and best.probability < float("inf"):
                joint_prob *= best.probability

        joint_label = f"{joint_prob:.2e}" if not is_blocked else f"BLOCKED ({blocked_by})"

        return DependencyResult(
            model=DependencyModel.A, tier=tier, measure=measure,
            groups=group_results,
            joint_probability=joint_prob if not is_blocked else float("nan"),
            joint_label=joint_label,
            is_blocked=is_blocked,
            block_reason=blocked_by,
            provenance=provenance,
        )

    def _model_b(self, tier: int, measure: MeasureType) -> DependencyResult:
        group_results = {}
        provenance = []
        joint_prob = 1.0
        is_blocked = False
        blocked_by = ""

        for group_name, group_spec in DEPENDENCY_GROUPS.items():
            eff_param = group_spec["effective_parameter"]
            members = group_spec["members"]

            relevant_tiers = [t for t in [tier, tier-1, tier-2] if t >= 1]
            best_overall = None

            for member in members:
                for rt in relevant_tiers:
                    result = self._best_bound(member, rt, measure)
                    if result is not None:
                        if best_overall is None or result.probability < best_overall.probability:
                            best_overall = result

            if best_overall is None:
                if eff_param == "mu_e_over_m_p":
                    group_results[group_name] = ProbabilityResult(
                        constant=eff_param, tier=tier, measure=measure,
                        bound_low=float("nan"), bound_high=float("nan"),
                        prior_low=float("nan"), prior_high=float("nan"),
                        probability=float("nan"),
                        probability_label=f"Group 2: μ has no bound → contributes factor 1",
                        provenance=[], is_measure_dominated=False,
                        is_blocked=False,
                    )
                    continue
                else:
                    group_results[group_name] = ProbabilityResult(
                        constant=eff_param, tier=tier, measure=measure,
                        bound_low=float("nan"), bound_high=float("nan"),
                        prior_low=float("nan"), prior_high=float("nan"),
                        probability=float("nan"),
                        probability_label=f"NO BOUND for {eff_param}",
                        provenance=[], is_measure_dominated=False,
                        is_blocked=True, block_reason=f"No bound for {eff_param}",
                    )
                    is_blocked = True
                    blocked_by = f"No bound for {eff_param}"
                    continue

            group_results[group_name] = best_overall
            provenance.extend(best_overall.provenance)
            if not best_overall.is_blocked and best_overall.probability < float("inf"):
                joint_prob *= best_overall.probability

        joint_label = f"{joint_prob:.2e}" if not is_blocked else f"BLOCKED ({blocked_by})"

        return DependencyResult(
            model=DependencyModel.B, tier=tier, measure=measure,
            groups=group_results,
            joint_probability=joint_prob if not is_blocked else float("nan"),
            joint_label=joint_label,
            is_blocked=is_blocked,
            block_reason=blocked_by,
            provenance=provenance,
        )

    def _model_c(self, tier: int, measure: MeasureType) -> DependencyResult:
        result_b = self._model_b(tier, measure)

        propagated_groups = {}
        for gname, gspec in DEPENDENCY_GROUPS.items():
            if gname not in result_b.groups:
                continue
            original = result_b.groups[gname]
            propagated_groups[gname] = original

        propagated_groups["_note"] = ProbabilityResult(
            constant="system", tier=tier, measure=measure,
            bound_low=float("nan"), bound_high=float("nan"),
            prior_low=float("nan"), prior_high=float("nan"),
            probability=float("nan"),
            probability_label="Model C converges to Model B — subsystem constraints are hierarchical",
            provenance=[],
            is_measure_dominated=False,
            is_blocked=False,
        )

        return DependencyResult(
            model=DependencyModel.C, tier=tier, measure=measure,
            groups=propagated_groups,
            joint_probability=result_b.joint_probability,
            joint_label=result_b.joint_label + f" (C ≡ B for hierarchical subsystems)",
            is_blocked=result_b.is_blocked,
            block_reason=result_b.block_reason,
            provenance=result_b.provenance + ["Model C: hierarchical subsystem propagation applied"],
        )


@dataclass
class MatrixCell:
    tier: int
    model: DependencyModel
    measure: MeasureType
    result: DependencyResult


class FullMatrix:
    def __init__(self, database: BoundDatabase):
        self.database = database
        self.me = MeasureEngine(database)
        self.de = DependencyEngine(database, self.me)
        self.cells: List[MatrixCell] = []

    def compute_all(self):
        self.cells = []

        for model in DependencyModel:
            for tier in [1, 2, 3]:
                for measure in [MeasureType.LOG_UNIFORM, MeasureType.LINEAR, MeasureType.AGNOSTIC]:
                    result = self.de.compute(model, tier, measure)
                    self.cells.append(MatrixCell(
                        tier=tier, model=model, measure=measure, result=result,
                    ))
        return self.cells

    def to_json(self, path: str):
        output = {
            "metadata": {
                "description": "Fine-tuning probability matrix from T300 analysis",
                "dependencies": {
                    "T300.2": "anthropic_bound_database.csv",
                    "T300.3": "dependency_graph.md",
                    "T300.4": "measure_audit.md",
                },
                "source_corpus_size": len(self.database.bounds),
            },
            "results": [],
        }

        for cell in self.cells:
            cell_dict = {
                "tier": cell.tier,
                "tier_name": TIER_DESCRIPTIONS.get(cell.tier, f"Tier {cell.tier}"),
                "model": cell.model.value,
                "measure": cell.measure.value,
                "joint_probability": cell.result.joint_probability,
                "joint_label": cell.result.joint_label,
                "is_blocked": cell.result.is_blocked,
                "block_reason": cell.result.block_reason,
                "groups": {},
            }
            for gname, grp in cell.result.groups.items():
                cell_dict["groups"][gname] = {
                    "constant": grp.constant,
                    "probability": grp.probability,
                    "probability_label": grp.probability_label,
                    "bound_low": grp.bound_low,
                    "bound_high": grp.bound_high,
                    "prior_low": grp.prior_low,
                    "prior_high": grp.prior_high,
                    "is_blocked": grp.is_blocked,
                    "block_reason": grp.block_reason,
                    "is_measure_dominated": grp.is_measure_dominated,
                }
            output["results"].append(cell_dict)

        with open(path, "w") as f:
            json.dump(output, f, indent=2, default=str)

        return path

    def to_csv_summary(self, path: str):
        with open(path, "w") as f:
            f.write("tier,tier_name,model,measure,joint_probability,joint_label,is_blocked,block_reason\n")
            for cell in self.cells:
                tier_name = TIER_DESCRIPTIONS.get(cell.tier, f"Tier {cell.tier}")
                f.write(
                    f"{cell.tier},{tier_name},{cell.model.value},{cell.measure.value},"
                    f"{cell.result.joint_probability},{cell.result.joint_label},{cell.result.is_blocked},"
                    f"{cell.result.block_reason}\n"
                )
        return path


def load_default_database(csv_path: str = "T300.2_anthropic_bound_database.csv"):
    import os
    if not os.path.exists(csv_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, csv_path)
    return BoundDatabase(csv_path)
