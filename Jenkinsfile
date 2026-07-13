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
                    pip install -r requirements.txt -q || true
                    pip install allure-pytest pytest-html pytest-sugar -q
                '''
            }
        }

        stage('运行测试') {
            steps {
                sh '''
                    # 激活虚拟环境运行测试
                    . venv/bin/activate
                    rm -rf ./allure-results
                    PYTHONPATH=$PYTHONPATH:. pytest testcases/ --alluredir=./allure-results -v -p no:warnings
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