pipeline {
    agent any

    stages {
        stage('安装依赖') {
            steps {
                sh '''
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi
                    . venv/bin/activate
                    pip install --upgrade pip -q
                    pip install requests pytest allure-pytest pytest-html pytest-sugar -q
                    if [ -f "requirements.txt" ]; then
                        pip install -r requirements.txt -q || true
                    fi
                '''
            }
        }

        stage('运行测试') {
            steps {
                sh '''
                    . venv/bin/activate
                    rm -rf ./allure-results
                    PYTHONPATH=$PYTHONPATH:. pytest testcases/test_visits testcases/test_time_analysis --alluredir=./allure-results -v
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
                // 发送飞书通知
                sh """
                    . venv/bin/activate
                    python utils/send_feishu.py \
                        "https://open.feishu.cn/open-apis/bot/v2/hook/e44589a8-9547-4710-97ee-d46246466160" \
                        "SUCCESS" \
                        "${env.JOB_NAME}" \
                        "${env.BUILD_NUMBER}" \
                        "${env.BUILD_URL}" \
                        "${env.BUILD_URL}allure"
                """
            }
        }
        failure {
            script {
                echo "❌ 测试失败！请查看日志: ${env.BUILD_URL}console"
                // 发送飞书通知
                sh """
                    . venv/bin/activate
                    python utils/send_feishu.py \
                        "https://open.feishu.cn/open-apis/bot/v2/hook/e44589a8-9547-4710-97ee-d46246466160" \
                        "FAILURE" \
                        "${env.JOB_NAME}" \
                        "${env.BUILD_NUMBER}" \
                        "${env.BUILD_URL}" \
                        "${env.BUILD_URL}allure"
                """
            }
        }
    }
}