# Expression-safe floor authoring for Post 2.
# Last line must remain an expression for eval-final-line executors.

from pxr import Gf, Usd, UsdGeom

floor_path = "/World/PalletizingCell/Floor"
UsdGeom.Xform.Define(stage, "/World/PalletizingCell")

if stage.GetPrimAtPath(floor_path).IsValid():
    stage.RemovePrim(floor_path)

floor = UsdGeom.Cube.Define(stage, floor_path)
floor.GetSizeAttr().Set(1.0)
UsdGeom.Xformable(floor.GetPrim()).AddScaleOp(
    UsdGeom.XformOp.PrecisionFloat
).Set(Gf.Vec3f(800.0, 600.0, 2.0))

prim = stage.GetPrimAtPath(floor_path)
valid = bool(prim.IsValid())
type_ok = prim.GetTypeName() == "Cube"
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
size = cache.ComputeWorldBound(prim).ComputeAlignedBox().GetSize()
result = {
    "status": "ok" if valid and type_ok else "failed",
    "path": floor_path,
    "checks": {
        "prim_valid": valid,
        "type_is_cube": type_ok,
        "extent_nonzero": float(size[0]) > 0.0 and float(size[1]) > 0.0,
    },
    "evidence": {
        "type_name": prim.GetTypeName(),
        "size_stage": [float(size[0]), float(size[1]), float(size[2])],
    },
}
result
