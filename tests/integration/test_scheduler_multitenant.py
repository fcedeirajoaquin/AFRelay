import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
class TestSchedulerMultiTenant:
    async def test_iterates_all_cuit_dirs(self, tmp_path):
        certs_dir = tmp_path / "certs"
        cuit1_dir = certs_dir / "20304050607"
        cuit2_dir = certs_dir / "27123456789"
        cuit1_dir.mkdir(parents=True)
        cuit2_dir.mkdir(parents=True)

        mock_generate = AsyncMock(return_value={"status": "success"})

        with patch("service.utils.afip_token_scheduler.Path", return_value=certs_dir), \
             patch("service.utils.afip_token_scheduler.generate_afip_access_token", mock_generate), \
             patch("service.utils.afip_token_scheduler.xml_exists", return_value=False):

            from service.utils.afip_token_scheduler import run_job
            await run_job()

        assert mock_generate.call_count == 2
        called_cuits = sorted([call.args[0] for call in mock_generate.call_args_list])
        assert called_cuits == ["20304050607", "27123456789"]

    async def test_partial_failure_does_not_block(self, tmp_path):
        certs_dir = tmp_path / "certs"
        (certs_dir / "20304050607").mkdir(parents=True)
        (certs_dir / "27123456789").mkdir(parents=True)

        call_count = {"value": 0}

        async def side_effect(cuit):
            call_count["value"] += 1
            if cuit == "20304050607":
                raise Exception("WSAA error")
            return {"status": "success"}

        with patch("service.utils.afip_token_scheduler.Path", return_value=certs_dir), \
             patch("service.utils.afip_token_scheduler.generate_afip_access_token", side_effect=side_effect), \
             patch("service.utils.afip_token_scheduler.xml_exists", return_value=False):

            from service.utils.afip_token_scheduler import run_job
            await run_job()

        assert call_count["value"] == 2

    async def test_skips_non_directory_entries(self, tmp_path):
        certs_dir = tmp_path / "certs"
        certs_dir.mkdir(parents=True)
        (certs_dir / "some_file.txt").write_text("not a dir")
        (certs_dir / "20304050607").mkdir()

        mock_generate = AsyncMock(return_value={"status": "success"})

        with patch("service.utils.afip_token_scheduler.Path", return_value=certs_dir), \
             patch("service.utils.afip_token_scheduler.generate_afip_access_token", mock_generate), \
             patch("service.utils.afip_token_scheduler.xml_exists", return_value=False):

            from service.utils.afip_token_scheduler import run_job
            await run_job()

        assert mock_generate.call_count == 1

    async def test_no_certs_dir_skips_gracefully(self, tmp_path):
        nonexistent = tmp_path / "nonexistent"

        with patch("service.utils.afip_token_scheduler.Path", return_value=nonexistent):
            from service.utils.afip_token_scheduler import run_job
            await run_job()
