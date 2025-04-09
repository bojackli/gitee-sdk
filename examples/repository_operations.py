"""Gitee SDK 仓库操作示例。

本示例展示了如何使用Gitee SDK进行仓库的基本操作，包括：
- 创建新仓库
- 获取仓库信息
- 更新仓库设置
- 删除仓库
"""

import logging
from gitee import GiteeClient
from gitee.exceptions import GiteeException

# 初始化Gitee客户端
# 请替换为你的访问令牌
ACCESS_TOKEN = "87fc372188a81d0efd3fcb3863a2154d"
client = GiteeClient(ACCESS_TOKEN)


def main():
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        # 创建新仓库
        logger.info("开始创建新仓库")
        print("创建新仓库...")
        new_repo = client.repositories.create(
            name="test-repo",
            description="这是一个测试仓库",
            private=True,
            auto_init=True,
            gitignore_template="Python",
            license_template="MIT"
        )
        logger.info(f"仓库创建成功: {new_repo['full_name']}")
        print(f"仓库创建成功: {new_repo['full_name']}\n")

        # 获取仓库信息
        repo_owner = new_repo['owner']['login']
        repo_name = new_repo['name']
        print(f"获取仓库 {repo_owner}/{repo_name} 的信息...")
        repo_info = client.repositories.get(repo_owner, repo_name)
        logger.info(
            f"获取到仓库信息 - 描述: {repo_info['description']}, 可见性: {'私有' if repo_info['private'] else '公开'}")
        print(f"仓库描述: {repo_info['description']}")
        print(f"仓库可见性: {'私有' if repo_info['private'] else '公开'}\n")

        # 更新仓库设置
        print("更新仓库设置...")
        new_name = 'new_' + repo_name
        updated_repo = client.repositories.update(
            owner=repo_owner,
            repo=repo_name,
            name=new_name,
            description="这是更新后的仓库描述",
            has_issues=True,
            has_wiki=True
        )
        logger.info(f"仓库更新成功: {updated_repo['description']}")
        print(f"仓库更新成功: {updated_repo['description']}\n")

        # 获取仓库分支
        print("获取仓库分支...")
        branches = client.repositories.list_branches(repo_owner, repo_name)
        logger.info(f"获取到仓库分支: {[branch['name'] for branch in branches]}")
        print(f"仓库分支列表: {[branch['name'] for branch in branches]}\n")

        # 获取仓库协作者
        print("获取仓库协作者...")
        collaborators = client.repositories.list_collaborators(repo_owner, repo_name)
        logger.info(f"获取到仓库协作者: {[collab['login'] for collab in collaborators]}")
        print(f"仓库协作者: {[collab['login'] for collab in collaborators]}\n")

        # 删除仓库
        print("删除仓库...")
        client.repositories.delete(repo_owner, repo_name)
        logger.info("仓库删除成功")
        print("仓库删除成功")

    except GiteeException as e:
        logger.error(f"操作失败: {e}")
        print(f"操作失败: {e}")


if __name__ == "__main__":
    main()
