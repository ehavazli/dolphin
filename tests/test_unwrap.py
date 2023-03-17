from pathlib import Path

import numpy as np
import pytest

from dolphin import io, unwrap


@pytest.fixture
def corr_raster(raster_100_by_200):
    # Make a correlation raster of all 1s in the same directory as the raster
    d = Path(raster_100_by_200).parent
    corr_raster = d / "corr_raster.bin"
    io.write_arr(
        arr=np.ones((100, 200), dtype=np.float32),
        output_name=corr_raster,
        like_filename=raster_100_by_200,
        driver="ENVI",
    )
    return corr_raster


def test_unwrap(tmp_path, raster_100_by_200, corr_raster):
    unw_filename = tmp_path / "unwrapped.unw.tif"
    unw_path, conncomp_path = unwrap.unwrap(
        ifg_filename=raster_100_by_200,
        corr_filename=corr_raster,
        unw_filename=unw_filename,
        nlooks=1,
        init_method="mst",
    )
    assert unw_path == unw_filename
    assert str(conncomp_path) == str(unw_filename).replace(".unw.tif", ".unw.conncomp")
    assert io.get_raster_xysize(unw_filename) == io.get_raster_xysize(raster_100_by_200)

    # test other init_method
    unw_path, conncomp_path = unwrap.unwrap(
        ifg_filename=raster_100_by_200,
        corr_filename=corr_raster,
        unw_filename=unw_filename,
        nlooks=1,
        init_method="mcf",
    )


def test_unwrap_logfile(tmp_path, raster_100_by_200, corr_raster):
    unw_filename = tmp_path / "unwrapped.unw.tif"
    unwrap.unwrap(
        ifg_filename=raster_100_by_200,
        corr_filename=corr_raster,
        unw_filename=unw_filename,
        nlooks=1,
        init_method="mst",
        log_to_file=True,
    )
    logfile_name = str(unw_filename).replace(".unw.tif", ".unw.log")
    assert Path(logfile_name).exists()


@pytest.fixture
def list_of_ifgs(tmp_path, raster_100_by_200):
    ifg_list = []
    for i in range(3):
        # Create a copy of the raster in the same directory
        f = tmp_path / f"ifg_{i}.int"
        ifg_list.append(f)
        io.write_arr(
            arr=np.ones((100, 200), dtype=np.complex64),
            output_name=f,
            like_filename=raster_100_by_200,
            driver="ENVI",
        )
        ifg_list.append(f)

    return ifg_list


@pytest.mark.parametrize("unw_suffix", [".unw", ".unw.tif"])
def test_run(list_of_ifgs, corr_raster, unw_suffix):
    ifg_path = list_of_ifgs[0].parent
    out_files, conncomp_files = unwrap.run(
        ifg_path=ifg_path,
        output_path=ifg_path,
        cor_file=corr_raster,
        nlooks=1,
        init_method="mst",
        ifg_suffix=".int",
        unw_suffix=unw_suffix,
        max_jobs=1,
    )


@pytest.fixture
def list_of_gtiff_ifgs(tmp_path, raster_100_by_200):
    ifg_list = []
    for i in range(3):
        # Create a copy of the raster in the same directory
        f = tmp_path / f"ifg_{i}.int.tif"
        io.write_arr(
            arr=np.ones((100, 200), dtype=np.complex64),
            output_name=f,
            like_filename=raster_100_by_200,
            driver="GTiff",
        )
        ifg_list.append(f)

    return ifg_list


@pytest.mark.parametrize("unw_suffix", [".unw", ".unw.tif"])
def test_run_gtiff(list_of_gtiff_ifgs, corr_raster, unw_suffix):
    ifg_path = list_of_gtiff_ifgs[0].parent
    out_files, conncomp_files = unwrap.run(
        ifg_path=ifg_path,
        output_path=ifg_path,
        cor_file=corr_raster,
        nlooks=1,
        init_method="mst",
        ifg_suffix=".int.tif",
        unw_suffix=unw_suffix,
        max_jobs=1,
    )
