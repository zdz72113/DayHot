#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MkDocs网站构建脚本
用于构建和部署GitHub Trending网站
"""

import os
import subprocess
import logging
import sys
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MkDocsBuilder:
    """MkDocs网站构建器"""
    
    def __init__(self):
        self.docs_dir = "mkdocs"
        self.site_dir = "site"
        self.config_file = "mkdocs.yml"
    
    def build_site(self) -> bool:
        """
        构建MkDocs网站
        
        Returns:
            构建是否成功
        """
        try:
            logger.info("开始构建MkDocs网站...")
            
            # 检查MkDocs是否安装
            if not self._check_mkdocs_installed():
                logger.error("MkDocs未安装，请运行: pip install mkdocs mkdocs-material")
                return False
            
            # 检查配置文件是否存在
            if not os.path.exists(self.config_file):
                logger.error(f"配置文件不存在: {self.config_file}")
                return False
            
            # 检查文档目录是否存在
            if not os.path.exists(self.docs_dir):
                logger.error(f"文档目录不存在: {self.docs_dir}")
                return False
            
            # 构建网站
            cmd = ["mkdocs", "build", "--clean"]
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                logger.info("MkDocs网站构建成功！")
                logger.info(f"网站文件位于: {os.path.abspath(self.site_dir)}")
                return True
            else:
                logger.error(f"MkDocs构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"构建网站时出错: {e}")
            return False
    
    def serve_site(self, host: str = "127.0.0.1", port: int = 8000) -> bool:
        """
        启动本地开发服务器
        
        Args:
            host: 主机地址
            port: 端口号
            
        Returns:
            启动是否成功
        """
        try:
            logger.info(f"启动MkDocs开发服务器: http://{host}:{port}")
            
            cmd = ["mkdocs", "serve", "--dev-addr", f"{host}:{port}"]
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 启动服务器（不阻塞）
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"开发服务器已启动，进程ID: {process.pid}")
            logger.info(f"访问地址: http://{host}:{port}")
            
            return True
            
        except Exception as e:
            logger.error(f"启动开发服务器时出错: {e}")
            return False
    
    def deploy_to_github_pages(self) -> bool:
        """
        部署到GitHub Pages
        
        Returns:
            部署是否成功
        """
        try:
            logger.info("开始部署到GitHub Pages...")
            
            # 检查是否在Git仓库中
            if not self._is_git_repo():
                logger.error("当前目录不是Git仓库")
                return False
            
            # 构建网站
            if not self.build_site():
                return False
            
            # 部署到GitHub Pages
            cmd = ["mkdocs", "gh-deploy", "--force"]
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                logger.info("成功部署到GitHub Pages！")
                return True
            else:
                logger.error(f"部署失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"部署到GitHub Pages时出错: {e}")
            return False
    
    def _check_mkdocs_installed(self) -> bool:
        """检查MkDocs是否已安装"""
        try:
            result = subprocess.run(
                ["mkdocs", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _is_git_repo(self) -> bool:
        """检查当前目录是否为Git仓库"""
        return os.path.exists(".git")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MkDocs网站构建工具")
    parser.add_argument("action", choices=["build", "serve", "deploy"], 
                       help="要执行的操作")
    parser.add_argument("--host", default="127.0.0.1", help="开发服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="开发服务器端口")
    
    args = parser.parse_args()
    
    builder = MkDocsBuilder()
    
    if args.action == "build":
        success = builder.build_site()
        sys.exit(0 if success else 1)
    elif args.action == "serve":
        success = builder.serve_site(args.host, args.port)
        sys.exit(0 if success else 1)
    elif args.action == "deploy":
        success = builder.deploy_to_github_pages()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

