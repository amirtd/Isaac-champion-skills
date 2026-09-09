# Post 3 demonstration: same physical floor on two unit metadatas.
# Do not call SetStageMetersPerUnit on a live Isaac Sim stage unless that
# change is an accepted plan step. Requires pxr (Kit session).

from pxr import Gf, Usd, UsdGeom

FLOOR = "/World/PalletizingCell/Floor"


def author_floor(stage, floor_path, length_m, width_m, thickness_m):
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    length_u = length_m / mpu
    width_u = width_m / mpu
    thick_u = thickness_m / mpu
    if stage.GetPrimAtPath(floor_path).IsValid():
        stage.RemovePrim(floor_path)
    cube = UsdGeom.Cube.Define(stage, floor_path)
    cube.GetSizeAttr().Set(1.0)
    xf = UsdGeom.Xformable(cube.GetPrim())
    xf.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(
        Gf.Vec3f(float(length_u), float(width_u), float(thick_u))
    )
    xf.AddTranslateOp(UsdGeom.XformOp.PrecisionFloat).Set(
        Gf.Vec3f(0.0, 0.0, float(thick_u) * 0.5)
    )


def world_size_m(stage, prim_path):
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    prim = stage.GetPrimAtPath(prim_path)
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    size = cache.ComputeWorldBound(prim).ComputeAlignedBox().GetSize()
    return (float(size[0]) * mpu, float(size[1]) * mpu, float(size[2]) * mpu)


def demo():
    cm_stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageMetersPerUnit(cm_stage, 0.01)
    UsdGeom.SetStageUpAxis(cm_stage, UsdGeom.Tokens.z)
    UsdGeom.Xform.Define(cm_stage, "/World/PalletizingCell")
    author_floor(cm_stage, FLOOR, 8.0, 6.0, 0.02)

    m_stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageMetersPerUnit(m_stage, 1.0)
    UsdGeom.SetStageUpAxis(m_stage, UsdGeom.Tokens.z)
    UsdGeom.Xform.Define(m_stage, "/World/PalletizingCell")
    author_floor(m_stage, FLOOR, 8.0, 6.0, 0.02)

    cm_size = world_size_m(cm_stage, FLOOR)
    m_size = world_size_m(m_stage, FLOOR)
    tol_m = 0.01
    return {
        "cm_stage_size_m": list(cm_size),
        "m_stage_size_m": list(m_size),
        "physical_match": all(abs(a - b) <= tol_m for a, b in zip(cm_size, m_size)),
        "expected_m": [8.0, 6.0, 0.02],
    }


if __name__ == "__main__":
    print(demo())
