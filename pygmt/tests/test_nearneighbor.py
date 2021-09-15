"""
Tests for nearneighbor.
"""
import os

import numpy.testing as npt
import pytest
import xarray as xr
from pygmt import nearneighbor
from pygmt.datasets import load_sample_bathymetry
from pygmt.exceptions import GMTInvalidInput
from pygmt.helpers import GMTTempFile, data_kind


@pytest.fixture(scope="module", name="ship_data")
def fixture_ship_data():
    """
    Load the data from the sample bathymetry dataset.
    """
    return load_sample_bathymetry()


def test_nearneighbor_input_file():
    """
    Run nearneighbor by passing in a filename.
    """
    output = nearneighbor(
        data="@tut_ship.xyz",
        spacing="5m",
        region=[245, 255, 20, 30],
        search_radius="10m",
    )
    assert isinstance(output, xr.DataArray)
    assert output.gmt.registration == 0  # Gridline registration
    assert output.gmt.gtype == 0  # Cartesian type
    assert output.shape == (121, 121)
    npt.assert_allclose(output.mean(), -2378.2385)
    return output


def test_nearneighbor_input_numpy_array(ship_data):
    """
    Run nearneighbor by passing in a numpy array into data.
    """
    data = ship_data.values  # convert pandas.DataFrame to numpy.ndarray
    output = nearneighbor(
        data=data, spacing="5m", region=[245, 255, 20, 30], search_radius="10m"
    )
    assert isinstance(output, xr.DataArray)
    assert output.shape == (121, 121)
    npt.assert_allclose(output.mean(), -2378.2385)
    return output


def test_nearneighbor_input_xyz(ship_data):
    """
    Run nearneighbor by passing in x, y, z numpy.ndarrays individually.
    """
    output = nearneighbor(
        x=ship_data.longitude,
        y=ship_data.latitude,
        z=ship_data.bathymetry,
        spacing="5m",
        region=[245, 255, 20, 30],
        search_radius="10m",
    )
    assert isinstance(output, xr.DataArray)
    assert output.shape == (121, 121)
    npt.assert_allclose(output.mean(), -2378.2385)
    return output


def test_nearneighbor_input_xy_no_z(ship_data):
    """
    Run nearneighbor by passing in x and y, but no z.
    """
    with pytest.raises(GMTInvalidInput):
        nearneighbor(
            x=ship_data.longitude,
            y=ship_data.latitude,
            spacing="5m",
            region=[245, 255, 20, 30],
            search_radius="10m",
        )


def test_nearneighbor_wrong_kind_of_input(ship_data):
    """
    Run nearneighbor using grid input that is not file/matrix/vectors.
    """
    data = ship_data.bathymetry.to_xarray()  # convert pandas.Series to xarray.DataArray
    assert data_kind(data) == "grid"
    with pytest.raises(GMTInvalidInput):
        nearneighbor(
            data=data, spacing="5m", region=[245, 255, 20, 30], search_radius="10m"
        )


def test_nearneighbor_with_outgrid_param(ship_data):
    """
    Run nearneighbor with the -Goutputfile.nc parameter.
    """
    data = ship_data.values  # convert pandas.DataFrame to numpy.ndarray
    with GMTTempFile() as tmpfile:
        output = nearneighbor(
            data=data,
            spacing="5m",
            region=[245, 255, 20, 30],
            outgrid=tmpfile.name,
            search_radius="10m",
        )
        assert output is None  # check that output is None since outgrid is set
        assert os.path.exists(path=tmpfile.name)  # check that outgrid exists at path
        with xr.open_dataarray(tmpfile.name) as grid:
            assert isinstance(grid, xr.DataArray)  # ensure netcdf grid loads ok
            assert grid.shape == (121, 121)
            npt.assert_allclose(grid.mean(), -2378.2385)
    return output
