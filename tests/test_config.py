from tidal_blade_test_analysis.config import ProjectPaths


def test_project_paths_are_under_root(tmp_path):
    paths = ProjectPaths.from_root(tmp_path)
    paths.make_dirs()
    assert paths.raw.exists()
    assert paths.interim.exists()
    assert paths.processed.exists()
    assert paths.results.exists()
