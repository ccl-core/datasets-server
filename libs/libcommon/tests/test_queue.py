# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The HuggingFace Authors.

from typing import Optional

import pytest

from libcommon.queue import EmptyQueueError, Queue, Status, _clean_queue_database


@pytest.fixture(autouse=True)
def clean_mongo_database() -> None:
    _clean_queue_database()


def test_add_job() -> None:
    test_type = "test_type"
    test_dataset = "test_dataset"
    # get the queue
    queue = Queue(test_type)
    # add a job
    queue.add_job(dataset=test_dataset, force=True)
    # a second call adds a second waiting job
    queue.add_job(dataset=test_dataset)
    assert queue.is_job_in_process(dataset=test_dataset) is True
    # get and start the first job
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == test_dataset
    assert started_job_info["config"] is None
    assert started_job_info["split"] is None
    assert started_job_info["force"] is True
    assert queue.is_job_in_process(dataset=test_dataset) is True
    # adding the job while the first one has not finished yet adds another waiting job
    # (there are no limits to the number of waiting jobs)
    queue.add_job(dataset=test_dataset, force=True)
    with pytest.raises(EmptyQueueError):
        # but: it's not possible to start two jobs with the same arguments
        queue.start_job()
    # finish the first job
    queue.finish_job(job_id=started_job_info["job_id"], finished_status=Status.SUCCESS)
    # the queue is not empty
    assert queue.is_job_in_process(dataset=test_dataset) is True
    # process the second job
    started_job_info = queue.start_job()
    assert started_job_info["force"] is False
    queue.finish_job(job_id=started_job_info["job_id"], finished_status=Status.SUCCESS)
    # and the third one
    started_job_info = queue.start_job()
    assert started_job_info["force"] is True
    other_job_id = ("1" if started_job_info["job_id"][0] == "0" else "0") + started_job_info["job_id"][1:]
    # trying to finish another job fails silently (with a log)
    queue.finish_job(job_id=other_job_id, finished_status=Status.SUCCESS)
    # finish it
    queue.finish_job(job_id=started_job_info["job_id"], finished_status=Status.SUCCESS)
    # the queue is empty
    assert queue.is_job_in_process(dataset=test_dataset) is False
    with pytest.raises(EmptyQueueError):
        # an error is raised if we try to start a job
        queue.start_job()


def test_priority_to_non_started_datasets() -> None:
    test_type = "test_type"
    queue = Queue(test_type)
    queue.add_job(dataset="dataset1", config="config", split="split1")
    queue.add_job(dataset="dataset1", config="config", split="split1")
    queue.add_job(dataset="dataset1/dataset", config="config", split="split1")
    queue.add_job(dataset="dataset1", config="config", split="split2")
    queue.add_job(dataset="dataset2", config="config", split="split1")
    queue.add_job(dataset="dataset2", config="config", split="split2")
    queue.add_job(dataset="dataset3", config="config", split="split1")
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == "dataset1"
    assert started_job_info["split"] == "split1"
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == "dataset2"
    assert started_job_info["split"] == "split1"
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == "dataset3"
    assert started_job_info["split"] == "split1"
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == "dataset1/dataset"
    assert started_job_info["split"] == "split1"
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == "dataset2"
    assert started_job_info["split"] == "split2"
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == "dataset1"
    assert started_job_info["split"] == "split2"
    with pytest.raises(EmptyQueueError):
        # raises even if there is still a waiting job
        # (dataset="dataset1", config="config", split="split1")
        # because a job with the same arguments is already started
        queue.start_job()


@pytest.mark.parametrize("max_jobs_per_namespace", [(None), (-5), (0), (1), (2)])
def test_max_jobs_per_namespace(max_jobs_per_namespace: Optional[int]) -> None:
    test_type = "test_type"
    test_dataset = "test_dataset"
    test_config = "test_config"
    queue = Queue(test_type, max_jobs_per_namespace=max_jobs_per_namespace)
    queue.add_job(dataset=test_dataset, config=test_config, split="split1")
    assert queue.is_job_in_process(dataset=test_dataset, config=test_config, split="split1") is True
    queue.add_job(dataset=test_dataset, config=test_config, split="split2")
    queue.add_job(dataset=test_dataset, config=test_config, split="split3")
    started_job_info = queue.start_job()
    assert started_job_info["dataset"] == test_dataset
    assert started_job_info["config"] == test_config
    assert started_job_info["split"] == "split1"
    assert queue.is_job_in_process(dataset=test_dataset, config=test_config, split="split1") is True
    if max_jobs_per_namespace == 1:
        with pytest.raises(EmptyQueueError):
            queue.start_job()
        return
    started_job_info_2 = queue.start_job()
    assert started_job_info_2["split"] == "split2"
    if max_jobs_per_namespace == 2:
        with pytest.raises(EmptyQueueError):
            queue.start_job()
        return
    # max_jobs_per_namespace <= 0 and max_jobs_per_namespace == None are the same
    # finish the first job
    queue.finish_job(started_job_info["job_id"], finished_status=Status.SUCCESS)
    assert queue.is_job_in_process(dataset=test_dataset, config=test_config, split="split1") is False


def test_count_by_status() -> None:
    test_type = "test_type"
    test_other_type = "test_other_type"
    test_dataset = "test_dataset"
    queue = Queue(test_type)
    queue_other = Queue(test_other_type)

    expected_empty = {"waiting": 0, "started": 0, "success": 0, "error": 0, "cancelled": 0, "skipped": 0}
    expected_one_waiting = {"waiting": 1, "started": 0, "success": 0, "error": 0, "cancelled": 0, "skipped": 0}

    assert queue.get_jobs_count_by_status() == expected_empty
    assert queue_other.get_jobs_count_by_status() == expected_empty

    queue.add_job(dataset=test_dataset)

    assert queue.get_jobs_count_by_status() == expected_one_waiting
    assert queue_other.get_jobs_count_by_status() == expected_empty

    queue_other.add_job(dataset=test_dataset)

    assert queue.get_jobs_count_by_status() == expected_one_waiting
    assert queue_other.get_jobs_count_by_status() == expected_one_waiting