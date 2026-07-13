pipeline {
    agent any

    stages {
        stage('安装依赖') {
            steps {
                sh '''
                    # 创建虚拟环境（如果不存在）
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi
                    # 激活虚拟环境并安装依赖
                    . venv/bin/activate
                    pip install --upgrade pip -q
                    # 强制安装 requests 和 pytest
                    pip install requests pytest allure-pytest pytest-html pytest-sugar -q
                    # 如果有 requirements.txt 也安装
                    if [ -f "requirements.txt" ]; then
                        pip install -r requirements.txt -q || true
                    fi
                '''
            }
        }

        stage('运行测试') {
            steps {
                sh '''
                    # 激活虚拟环境运行测试
                    . venv/bin/activate
                    rm -rf ./allure-results
                    # 将项目根目录添加到 Python 路径，解决 config 模块找不到的问题
                    PYTHONPATH=$PYTHONPATH:. pytest testcases/test_visits/ --alluredir=./allure-results -s -v
                '''
            }
        }

        stage('生成 Allure 报告') {
            steps {
                script {
                    allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                }
            }
        }
    }

    post {
        success {
            script {
                echo "✅ 测试通过！报告地址: ${env.BUILD_URL}allure"
            }
        }
        failure {
            script {
                echo "❌ 测试失败！请查看日志: ${env.BUILD_URL}console"
            }
        }
    }
}