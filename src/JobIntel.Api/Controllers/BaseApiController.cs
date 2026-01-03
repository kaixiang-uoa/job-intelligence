using Microsoft.AspNetCore.Mvc;

namespace JobIntel.Api.Controllers;

/// <summary>
/// Base controller for all API endpoints
/// Provides common functionality and authentication readiness for V2
/// </summary>
[ApiController]
[Route("api/[controller]")]
// [Authorize] // 取消注释以启用认证 (V2)
public abstract class BaseApiController : ControllerBase
{
    /// <summary>
    /// V2: 获取当前认证用户的 ID
    /// 当前返回 null，V2 启用认证后从 Claims 中获取
    /// </summary>
    protected int? GetCurrentUserId()
    {
        // V1: 无认证，返回 null
        // V2: 从 User.Claims 中获取用户 ID
        // var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier);
        // return userIdClaim != null ? int.Parse(userIdClaim.Value) : null;
        return null;
    }

    /// <summary>
    /// V2: 检查当前用户是否已认证
    /// </summary>
    protected bool IsAuthenticated()
    {
        // V1: 始终返回 false
        // V2: return User.Identity?.IsAuthenticated ?? false;
        return false;
    }

    /// <summary>
    /// 创建标准的成功响应
    /// </summary>
    protected ActionResult<T> Success<T>(T data)
    {
        return Ok(data);
    }

    /// <summary>
    /// 创建标准的错误响应
    /// </summary>
    protected ActionResult<T> Error<T>(string message, int statusCode = 400)
    {
        return StatusCode(statusCode, new { error = message });
    }
}
