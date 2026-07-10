###############################################################################
#  Avatar 头像预览 API — 供 ai_leader_dig 后端代理获取头像图片
###############################################################################

import os
import glob
import logging

from aiohttp import web

from utils.logger import logger


def json_ok(data=None):
    body = {"code": 0, "msg": "ok"}
    if data is not None:
        body["data"] = data
    return web.json_response(body)


def json_error(msg: str, code: int = -1, status: int = 200):
    return web.json_response(
        {"code": code, "msg": str(msg)},
        status=status,
    )


async def avatar_preview(request):
    """GET /api/avatars/{avatar_id}/preview
    返回指定 avatar 文件夹 full_imgs/ 下的第一张 PNG 预览图
    """
    avatar_id = request.match_info.get('avatar_id', '')
    if not avatar_id:
        return json_error("avatar_id is required", status=400)

    full_imgs_dir = os.path.join('data', 'avatars', avatar_id, 'full_imgs')

    # 安全检查：防止路径遍历
    safe_dir = os.path.normpath(os.path.join('data', 'avatars', avatar_id))
    if not safe_dir.startswith(os.path.normpath('data/avatars')):
        return json_error("非法路径", status=403)

    if not os.path.isdir(full_imgs_dir):
        return json_error("头像图片目录不存在", status=404)

    png_files = sorted(glob.glob(os.path.join(full_imgs_dir, '*.png')))
    if not png_files:
        return json_error("未找到头像图片", status=404)

    return web.FileResponse(png_files[0])


async def avatar_list(request):
    """GET /api/avatars
    返回 data/avatars/ 下所有可用的 avatar 文件夹列表
    """
    avatars_dir = os.path.join('data', 'avatars')
    result = []

    if os.path.isdir(avatars_dir):
        for name in sorted(os.listdir(avatars_dir)):
            full = os.path.join(avatars_dir, name)
            if not os.path.isdir(full):
                continue
            has_coords = os.path.isfile(os.path.join(full, 'coords.pkl'))
            has_latents = os.path.isfile(os.path.join(full, 'latents.pt'))
            has_imgs = os.path.isdir(os.path.join(full, 'full_imgs'))
            if has_coords or has_latents or has_imgs:
                result.append({
                    'folder': name,
                    'has_coords': has_coords,
                    'has_latents': has_latents,
                    'has_imgs': has_imgs,
                })

    return json_ok(data=result)


def setup_avatar_preview_routes(app):
    """注册头像预览相关路由"""
    app.router.add_get('/api/avatars/{avatar_id}/preview', avatar_preview)
    app.router.add_get('/api/avatars', avatar_list)
    logger.info("[AvatarPreview] Avatar preview routes registered")
