"""
项目设置验证脚本

在安装依赖后运行此脚本验证项目配置是否正确
"""

def verify_imports():
    """验证核心模块导入"""
    print("🔍 验证 Python 模块导入...")

    try:
        from app.models.job_posting_dto import (
            JobPostingDTO,
            PlatformEnum,
            ScrapeRequest,
            ScrapeResponse,
            HealthResponse
        )
        print("  ✅ 数据模型导入成功")
    except ImportError as e:
        print(f"  ❌ 数据模型导入失败: {e}")
        return False

    try:
        from app.adapters.base_adapter import BaseJobAdapter, ScraperException
        print("  ✅ 适配器基类导入成功")
    except ImportError as e:
        print(f"  ❌ 适配器基类导入失败: {e}")
        return False

    try:
        from app.config.settings import settings
        print("  ✅ 配置模块导入成功")
    except ImportError as e:
        print(f"  ❌ 配置模块导入失败: {e}")
        return False

    try:
        from app.main import app
        print("  ✅ FastAPI 应用导入成功")
    except ImportError as e:
        print(f"  ❌ FastAPI 应用导入失败: {e}")
        return False

    return True


def verify_config():
    """验证配置"""
    print("\n🔍 验证配置...")

    try:
        from app.config.settings import settings

        print(f"  ✅ App Name: {settings.app_name}")
        print(f"  ✅ Version: {settings.app_version}")
        print(f"  ✅ Debug Mode: {settings.debug}")
        print(f"  ✅ Supported Platforms: {', '.join(settings.supported_platforms)}")

        return True
    except Exception as e:
        print(f"  ❌ 配置验证失败: {e}")
        return False


def verify_structure():
    """验证项目结构"""
    print("\n🔍 验证项目结构...")

    import os

    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/models/__init__.py",
        "app/models/job_posting_dto.py",
        "app/adapters/__init__.py",
        "app/adapters/base_adapter.py",
        "app/config/__init__.py",
        "app/config/settings.py",
        "app/services/__init__.py",
        "app/utils/__init__.py",
        "requirements.txt",
        ".env",
        "README.md",
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} 缺失")
            all_exist = False

    return all_exist


def main():
    """主函数"""
    print("=" * 60)
    print("Job Intelligence Scraper API - 设置验证")
    print("=" * 60)

    results = []

    # 验证项目结构
    results.append(("项目结构", verify_structure()))

    # 验证导入
    results.append(("模块导入", verify_imports()))

    # 验证配置
    results.append(("配置管理", verify_config()))

    # 总结
    print("\n" + "=" * 60)
    print("验证结果总结")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 所有验证通过！项目配置正确。")
        print("\n下一步:")
        print("  1. 启动服务: ./run.sh 或 uvicorn app.main:app --reload")
        print("  2. 访问文档: http://localhost:8000/docs")
        print("  3. 测试健康检查: curl http://localhost:8000/health")
        return 0
    else:
        print("\n⚠️  部分验证失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    exit(main())
