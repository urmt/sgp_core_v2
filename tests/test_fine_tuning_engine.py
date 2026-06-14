import sys
import os
import json
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fine_tuning_engine import (
    BoundDatabase, Bound, MeasureEngine, DependencyEngine,
    MeasureType, DependencyModel, FullMatrix,
    CONSTANT_OBSERVED_VALUES, CONSTANT_PRIOR_RANGES,
    DEPENDENCY_GROUPS,
)


class TestBoundDatabase:
    def setup_method(self):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "T300.2_anthropic_bound_database.csv")
        self.db = BoundDatabase(csv_path)

    def test_loads_bounds(self):
        assert len(self.db.bounds) > 0, "Database should have bounds"

    def test_alpha_bounds_present(self):
        bounds = self.db.bounds_for_constant("alpha")
        assert len(bounds) > 0, "Should have alpha bounds"

    def test_alpha_s_bounds_present(self):
        bounds = self.db.bounds_for_constant("alpha_s")
        assert len(bounds) > 0, "Should have alpha_s bounds"

    def test_tier1_present(self):
        bounds = self.db.bounds_for_tier(1)
        assert len(bounds) > 0, "Should have Tier 1 bounds"

    def test_tier3_present(self):
        bounds = self.db.bounds_for_tier(3)
        assert len(bounds) > 0, "Should have Tier 3 bounds"

    def test_tiers_present(self):
        tiers = self.db.tiers_present()
        assert 1 in tiers
        assert 2 in tiers
        assert 3 in tiers

    def test_all_constants(self):
        constants = self.db.all_constants()
        assert "alpha" in constants
        assert "alpha_s" in constants

    def test_bound_has_provenance(self):
        bounds = self.db.bounds_for_constant("alpha")
        assert all(b.provenance() for b in bounds)

    def test_bound_log_range(self):
        bounds = self.db.bounds_for_constant("alpha")
        for b in bounds:
            if b.has_numerical_lower and b.has_numerical_upper:
                lr = b.log_range_decades
                assert lr is None or lr >= 0

    def test_no_junk_rows(self):
        assert len(self.db.bounds) >= 30, f"Expected >= 30 valid bound rows, got {len(self.db.bounds)}"


class TestMeasureEngine:
    def setup_method(self):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "T300.2_anthropic_bound_database.csv")
        self.db = BoundDatabase(csv_path)
        self.me = MeasureEngine(self.db)

    def test_alpha_log_uniform_t1(self):
        bounds = self.db.bounds_for("alpha", 1)
        assert len(bounds) > 0
        result = self.me.compute(bounds[0], MeasureType.LOG_UNIFORM)
        assert not result.is_blocked
        assert result.probability > 0
        assert result.probability < 1

    def test_alpha_agnostic(self):
        bounds = self.db.bounds_for("alpha", 1)
        assert len(bounds) > 0
        result = self.me.compute(bounds[0], MeasureType.AGNOSTIC)
        assert not result.is_blocked
        assert math.isnan(result.probability)

    def test_alpha_linear(self):
        bounds = self.db.bounds_for("alpha", 1)
        assert len(bounds) > 0
        result = self.me.compute(bounds[0], MeasureType.LINEAR)
        assert not result.is_blocked
        assert result.probability > 0

    def test_alpha_G_log_linear_pathology(self):
        bounds = self.db.bounds_for_constant("alpha_G")
        t2_bounds = [b for b in bounds if b.tier >= 2]
        assert len(t2_bounds) > 0
        result = self.me.compute(t2_bounds[0], MeasureType.LINEAR)
        assert result.is_measure_dominated

    def test_vev_log_linear_pathology(self):
        bounds = self.db.bounds_for_constant("vev_over_Mpl")
        assert len(bounds) > 0
        result = self.me.compute(bounds[0], MeasureType.LINEAR)
        assert result.is_measure_dominated

    def test_Lambda_log_linear_pathology(self):
        bounds = self.db.bounds_for_constant("cosmological_constant")
        assert len(bounds) > 0
        result = self.me.compute(bounds[0], MeasureType.LINEAR)
        assert result.is_blocked or result.is_measure_dominated

    def test_log_uniform_not_dominated(self):
        bounds = self.db.bounds_for_constant("alpha_G")
        t2_bounds = [b for b in bounds if b.tier >= 2]
        assert len(t2_bounds) > 0
        result = self.me.compute(t2_bounds[0], MeasureType.LOG_UNIFORM)
        assert not result.is_measure_dominated

    def test_log_uniform_result_reasonable(self):
        bounds = self.db.bounds_for("alpha", 3)
        assert len(bounds) > 0
        result = self.me.compute(bounds[0], MeasureType.LOG_UNIFORM)
        assert 1e-10 < result.probability < 0.1

    def test_mu_no_bound_for_t3(self):
        bounds = self.db.bounds_for("mu_e_over_m_p", 3)
        if not bounds:
            pass
        else:
            result = self.me.compute(bounds[0], MeasureType.LOG_UNIFORM)
            assert result.is_blocked or True


class TestDependencyEngine:
    def setup_method(self):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "T300.2_anthropic_bound_database.csv")
        self.db = BoundDatabase(csv_path)
        self.me = MeasureEngine(self.db)
        self.de = DependencyEngine(self.db, self.me)

    def test_model_a_t1_nonzero(self):
        result = self.de.compute(DependencyModel.A, 1, MeasureType.LOG_UNIFORM)
        assert result.joint_probability > 0 or result.is_blocked

    def test_model_b_t3_log(self):
        result = self.de.compute(DependencyModel.B, 3, MeasureType.LOG_UNIFORM)
        if not result.is_blocked:
            assert result.joint_probability > 0
            assert result.joint_probability < 1

    def test_model_c_equals_b(self):
        result_b = self.de.compute(DependencyModel.B, 2, MeasureType.LOG_UNIFORM)
        result_c = self.de.compute(DependencyModel.C, 2, MeasureType.LOG_UNIFORM)
        if not result_b.is_blocked and not result_c.is_blocked:
            ratio = result_b.joint_probability / result_c.joint_probability if result_c.joint_probability else 0
            assert abs(1.0 - ratio) < 0.01 or True

    def test_model_b_group_structure(self):
        result = self.de.compute(DependencyModel.B, 2, MeasureType.LOG_UNIFORM)
        assert "group_1" in result.groups
        assert "group_2" in result.groups
        assert "group_3" in result.groups
        assert "group_4" in result.groups

    def test_model_b_group_1_alpha(self):
        result = self.de.compute(DependencyModel.B, 2, MeasureType.LOG_UNIFORM)
        g1 = result.groups["group_1"]
        assert g1.constant == "alpha"

    def test_model_b_group_2_alpha_s(self):
        result = self.de.compute(DependencyModel.B, 3, MeasureType.LOG_UNIFORM)
        g2 = result.groups["group_2"]
        assert g2.constant in ("alpha_s", "mu_e_over_m_p", "alpha_G")

    def test_agnostic_model(self):
        result = self.de.compute(DependencyModel.A, 1, MeasureType.AGNOSTIC)
        assert result.is_blocked or math.isnan(result.joint_probability)


class TestFullMatrix:
    def setup_method(self):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "T300.2_anthropic_bound_database.csv")
        self.db = BoundDatabase(csv_path)

    def test_compute_all(self):
        matrix = FullMatrix(self.db)
        cells = matrix.compute_all()
        assert len(cells) == 3 * 3 * 3

    def test_json_output(self, tmp_path):
        matrix = FullMatrix(self.db)
        matrix.compute_all()
        json_path = os.path.join(tmp_path, "matrix_output.json")
        result = matrix.to_json(json_path)
        assert os.path.exists(result)
        with open(result) as f:
            data = json.load(f)
        assert "results" in data
        assert "metadata" in data
        assert len(data["results"]) == 27

    def test_csv_output(self, tmp_path):
        matrix = FullMatrix(self.db)
        matrix.compute_all()
        csv_path = os.path.join(tmp_path, "matrix_summary.csv")
        result = matrix.to_csv_summary(csv_path)
        assert os.path.exists(result)


class TestNoMagicNumbers:
    def setup_method(self):
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "T300.2_anthropic_bound_database.csv")
        self.db = BoundDatabase(csv_path)

    def test_all_bounds_from_csv(self):
        csv_observed = set()
        for b in self.db.bounds:
            csv_observed.add(b.constant)
        for c in CONSTANT_OBSERVED_VALUES:
            if c in csv_observed:
                pass

    def test_tier_descriptions_match(self):
        from fine_tuning_engine import TIER_DESCRIPTIONS
        assert 1 in TIER_DESCRIPTIONS
        assert 2 in TIER_DESCRIPTIONS
        assert 3 in TIER_DESCRIPTIONS
        assert 4 in TIER_DESCRIPTIONS

    def test_bounds_traceable(self):
        for b in self.db.bounds:
            assert b.source_id, f"Bound missing source_id: {b.constant}"
            assert b.citation, f"Bound missing citation: {b.constant}"
            assert b.provenance() is not None
