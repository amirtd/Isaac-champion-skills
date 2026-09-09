# Grounded floor define/replace for Post 1.
# Target: Isaac Sim 5.0 / OpenUSD 24.x. Requires a Kit-provided `stage`.
# Cube size is scalar. Rectangular extent is scale. Last line is an expression.

from pxr import Gf, Usd, UsdGeom

cell_path = "/World/PalletizingCell"
floor_path = "/World/PalletizingCell/Floor"

UsdGeom.Xform.Define(stage, cell_path)

existing = stage.GetPrimAtPath(floor_path)
if existing.IsValid():
    stage.RemovePrim(floor_path)

floor = UsdGeom.Cube.Define(stage, floor_path)
floor.GetSizeAttr().Set(1.0)
xform = UsdGeom.Xformable(floor.GetPrim())
xform.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(Gf.Vec3f(800.0, 600.0, 2.0))
xform.AddTranslateOp(UsdGeom.XformOp.PrecisionFloat).Set(Gf.Vec3f(0.0, 0.0, 1.0))

prim = stage.GetPrimAtPath(floor_path)
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
box = cache.ComputeWorldBound(prim).ComputeAlignedBox()
size = box.GetSize()
mpu = UsdGeom.GetStageMetersPerUnit(stage)

result = {
    "path": floor_path,
    "valid": bool(prim.IsValid()),
    "type_name": prim.GetTypeName(),
    "schema": "UsdGeomCube",
    "size_stage": [float(size[0]), float(size[1]), float(size[2])],
    "size_m": [float(size[0]) * mpu, float(size[1]) * mpu, float(size[2]) * mpu],
    "meters_per_unit": mpu,
}
result
