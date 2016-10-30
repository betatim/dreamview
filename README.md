# DreamView

Dreaming of map tiles.

Machine-learning experiments on aerial images and OSM data.


## Getting started

Download Bing aerial image tiles and metadata about each tile with:

```
python scripts/get_mapswipe_data.py 1 # 1 -> sets mapswipe project
```

This will fetch tiles for a subset of those for which mapswipe has a
positive rating. It will also fetch random tiles which do no appear
in the mapswipe dataset. These are assumed to be "boring".

Next reorganise the data a bit and train a CNN:
```
python scripts/build_data.py
python scripts/train_cnn.py
```

You can also train an extra trees classifier instead of a CNN:
```
python scripts/train_extratrees.py
```
This does not need to have the data prepared via `build_data.py`.


## Dependencies

You need python and `keras`.
