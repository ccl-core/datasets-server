# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The HuggingFace Authors.


from worker.job_runners.dataset.croissant_crumbs import (
    get_croissant_crumbs_from_dataset_infos,
)

squad_info = {
    "description": "Stanford Question Answering Dataset (SQuAD) is a reading comprehension dataset, consisting of questions posed by crowdworkers on a set of Wikipedia articles, where the answer to every question is a segment of text, or span, from the corresponding reading passage, or the question might be unanswerable.\n",
    "citation": '@article{2016arXiv160605250R,\n       author = {{Rajpurkar}, Pranav and {Zhang}, Jian and {Lopyrev},\n                 Konstantin and {Liang}, Percy},\n        title = "{SQuAD: 100,000+ Questions for Machine Comprehension of Text}",\n      journal = {arXiv e-prints},\n         year = 2016,\n          eid = {arXiv:1606.05250},\n        pages = {arXiv:1606.05250},\narchivePrefix = {arXiv},\n       eprint = {1606.05250},\n}\n',
    "homepage": "https://rajpurkar.github.io/SQuAD-explorer/",
    "license": ["mit"],
    "tags": ["foo", "doi:hf/123456789", "region:us"],
    "features": {
        "id": {"dtype": "string", "_type": "Value"},
        "title": {"dtype": "string", "_type": "Value"},
        "context": {"dtype": "string", "_type": "Value"},
        "question": {"dtype": "string", "_type": "Value"},
        "answers": {
            "text": {
                "feature": {"dtype": "string", "_type": "Value"},
                "_type": "List",
            },
            "answer_start": {
                "feature": {"dtype": "int32", "_type": "Value"},
                "_type": "List",
            },
        },
    },
    "task_templates": [{"task": "question-answering-extractive"}],
    "builder_name": "squad",
    "config_name": "user/squad with space",
    "version": {"version_str": "1.0.0", "description": "", "major": 1, "minor": 0, "patch": 0},
    "splits": {
        "train": {"name": "train", "num_bytes": 79346108, "num_examples": 87599, "dataset_name": "squad"},
        "validation": {
            "name": "validation",
            "num_bytes": 10472984,
            "num_examples": 10570,
            "dataset_name": "squad",
        },
    },
    "download_checksums": {
        "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json": {
            "num_bytes": 30288272,
            "checksum": None,
        },
        "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json": {
            "num_bytes": 4854279,
            "checksum": None,
        },
    },
    "download_size": 35142551,
    "dataset_size": 89819092,
    "size_in_bytes": 124961643,
}
squad_splits = ["train", "validation"]


v1_context = {
    "@language": "en",
    "@vocab": "https://schema.org/",
    "arrayShape": "cr:arrayShape",
    "citeAs": "cr:citeAs",
    "column": "cr:column",
    "conformsTo": "dct:conformsTo",
    "cr": "http://mlcommons.org/croissant/",
    "data": {"@id": "cr:data", "@type": "@json"},
    "dataBiases": "cr:dataBiases",
    "dataCollection": "cr:dataCollection",
    "dataType": {"@id": "cr:dataType", "@type": "@vocab"},
    "dct": "http://purl.org/dc/terms/",
    "extract": "cr:extract",
    "field": "cr:field",
    "fileProperty": "cr:fileProperty",
    "fileObject": "cr:fileObject",
    "fileSet": "cr:fileSet",
    "format": "cr:format",
    "includes": "cr:includes",
    "isArray": "cr:isArray",
    "isLiveDataset": "cr:isLiveDataset",
    "jsonPath": "cr:jsonPath",
    "key": "cr:key",
    "md5": "cr:md5",
    "parentField": "cr:parentField",
    "path": "cr:path",
    "personalSensitiveInformation": "cr:personalSensitiveInformation",
    "recordSet": "cr:recordSet",
    "references": "cr:references",
    "regex": "cr:regex",
    "repeated": "cr:repeated",
    "replace": "cr:replace",
    "sc": "https://schema.org/",
    "separator": "cr:separator",
    "source": "cr:source",
    "subField": "cr:subField",
    "transform": "cr:transform",
}


def test_get_croissant_context_from_dataset_infos() -> None:
    croissant_crumbs = get_croissant_crumbs_from_dataset_infos(
        "user/squad with space", [squad_info, squad_info], partial=False, truncated_configs=False
    )
    assert croissant_crumbs["@context"] == v1_context


def test_get_croissant_crumbs_from_dataset_infos() -> None:
    croissant_crumbs = get_croissant_crumbs_from_dataset_infos(
        "user/squad with space", [squad_info, squad_info], partial=False, truncated_configs=False
    )
    assert "@context" in croissant_crumbs
    assert "@type" in croissant_crumbs
    assert croissant_crumbs["conformsTo"] == "http://mlcommons.org/croissant/1.1"

    # Test recordSet.
    assert "recordSet" in croissant_crumbs
    assert croissant_crumbs["recordSet"]
    assert isinstance(croissant_crumbs["recordSet"], list)
    assert len(croissant_crumbs["recordSet"]) == 4

    # Test split record sets.
    for i in [0, 2]:
        assert "data" in croissant_crumbs["recordSet"][i]
        for d in croissant_crumbs["recordSet"][i]["data"]:
            for key in d.keys():
                if key.endswith("name"):
                    assert d[key] in squad_splits
        assert croissant_crumbs["recordSet"][i]["dataType"] == "cr:Split"
        assert croissant_crumbs["recordSet"][i]["key"]["@id"].endswith("name")
    assert croissant_crumbs["recordSet"][1]["@type"] == croissant_crumbs["recordSet"][3]["@type"] == "cr:RecordSet"
    assert isinstance(croissant_crumbs["recordSet"][1]["field"], list)
    assert isinstance(squad_info["features"], dict)
    assert "skipped column" not in croissant_crumbs["recordSet"][1]["description"]
    assert croissant_crumbs["recordSet"][1]["@id"] == "record_set_user_squad_with_space"
    assert croissant_crumbs["recordSet"][3]["@id"] == "record_set_user_squad_with_space_0"
    for i in [1, 3]:
        for field in croissant_crumbs["recordSet"][i]["field"]:
            if "subField" not in field:
                assert "source" in field
                assert "fileSet" in field["source"]
                assert "@id" in field["source"]["fileSet"]
                assert field["source"]["fileSet"]["@id"]
                assert "extract" in field["source"]
            else:
                for sub_field in field["subField"]:
                    assert "source" in sub_field
                    assert "fileSet" in sub_field["source"]
                    assert "@id" in sub_field["source"]["fileSet"]
                    assert sub_field["source"]["fileSet"]["@id"]
                    assert "extract" in sub_field["source"]
                    assert "transform" in sub_field["source"]
                    if "answer_start" in sub_field["@id"]:
                        assert sub_field["isArray"] is True
                        assert sub_field["arrayShape"] == "-1"
            if field["@id"].endswith("split"):
                assert "regex" in field["source"]["transform"]
                assert field["source"]["extract"]["fileProperty"] == "fullpath"
                assert field["references"]["field"]["@id"] == croissant_crumbs["recordSet"][i - 1]["field"][0]["@id"]
            else:
                if "subField" not in field:
                    assert field["source"]["extract"]["column"] == field["@id"].split("/")[-1]
                else:
                    for sub_field in field["subField"]:
                        assert sub_field["source"]["extract"]["column"] == field["@id"].split("/")[-1]

    # Test fields.
    assert len(croissant_crumbs["recordSet"][1]["field"]) == 6
    assert len(croissant_crumbs["recordSet"][3]["field"]) == 6
    for field in croissant_crumbs["recordSet"][1]["field"]:
        assert field["@type"] == "cr:Field"
        if "subField" not in field:
            assert field["dataType"] == "sc:Text"
    assert len(croissant_crumbs["recordSet"][1]["field"]) == len(squad_info["features"]) + 1

    # Test distribution.
    assert "distribution" in croissant_crumbs
    assert croissant_crumbs["distribution"]
    assert isinstance(croissant_crumbs["distribution"], list)
    assert croissant_crumbs["distribution"][0]["@type"] == "cr:FileObject"
    assert croissant_crumbs["distribution"][1]["@type"] == "cr:FileSet"
    assert croissant_crumbs["distribution"][2]["@type"] == "cr:FileSet"
    assert croissant_crumbs["distribution"][0]["name"] == "repo"
    for distribution in croissant_crumbs["distribution"]:
        assert "@id" in distribution
        if "containedIn" in distribution:
            assert "@id" in distribution["containedIn"]
