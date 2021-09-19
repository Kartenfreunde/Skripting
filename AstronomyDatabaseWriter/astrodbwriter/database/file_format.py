import os
from typing import List, Optional, Sequence, Dict, Any, cast

import ResourceBundle.BundleTypes.BasicResourceBundle as res
import geojson
import pathlib
import csv
from ResourceBundle.exceptions import NotInResourceBundleError
from ResourceBundle.util.Locale import Locale
from babel.numbers import format_decimal
from geojson import Feature, Point, FeatureCollection


def write_geojson(path: str, language: Optional[str], items: Sequence[Any]):
    features: List[Feature] = []
    for item in items:
        properties: Dict[str, object] = dict(item.__dict__)  # copy as we modify it below
        properties.pop("longitude")
        properties.pop("latitude")
        if language is not None:
            # fallback to untranslated for values, since they may contain e. g. names of
            # locations, which can and should not be translated
            properties = {_translate(k, language): _translate(v, language, True)
                          for k, v in properties.items()}
        features.append(Feature(geometry=Point((item.longitude, item.latitude)),
                        properties=properties))
    with open(path, 'w', newline='', encoding="utf-8") as file:
        geojson.dump(FeatureCollection(features), file, indent=2, default=str)


def write_csv(path: str, language: Optional[str], items: Sequence[Any]):
    # ensure argument validity
    if len(items) == 0:
        raise ValueError("Cannot write empty database file")
    first_type = type(items[0])
    if not all(isinstance(line, first_type) for line in items):
        raise ValueError("All line objects must be of same type")

    # write file
    with open(path, 'w', newline='', encoding="utf-8") as file:
        fieldnames = list(items[0].__dict__.keys())
        if language is not None:
            fieldnames = [_translate(f, language) for f in fieldnames]
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for item in items:
            row_dict: Dict[str, object] = item.__dict__
            if language is not None:
                # fallback to untranslated for values, since they may contain e. g. names of
                # locations, which can and should not be translated
                row_dict = {_translate(k, language): _translate(v, language, True)
                            for k, v in row_dict.items()}
            writer.writerow(row_dict)


_resource_bundle_cache: Dict[str, res.BasicResourceBundle] = {}


def _translate(value: object, language: str, fallback: bool = False) -> str:
    # first of all, format floats correctly by using the babel module
    if isinstance(value, float):
        return format_decimal(value, locale=language)

    # otherwise, check if we have a translation in a resource file for this
    if language not in _resource_bundle_cache:
        translations_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "translations")
        _resource_bundle_cache[language] = cast(res.BasicResourceBundle,
                                                res.get_bundle(translations_path, Locale(language)))
    resource_bundle = _resource_bundle_cache[language]

    try:
        return resource_bundle.get(str(value))
    except NotInResourceBundleError as error:
        if fallback:
            return str(value)
        raise error
