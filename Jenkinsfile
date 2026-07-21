pipeline {
    agent any

    environment {
        // GitHub Pages 上永久可访问的 Allure 报告地址（不依赖 Jenkins 外网可达）
        PAGES_URL   = 'https://jinbanzhuan.github.io/xiaobei/'
        // Allure CLI 缓存目录（避免每次构建重新下载）
        ALLURE_HOME = "${env.HOME}/.allure/allure-2.30.0"
    }

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

                    # Allure CLI（Java-based），首次构建自动下载
                    if [ ! -x "${ALLURE_HOME}/bin/allure" ]; then
                        mkdir -p "$(dirname ${ALLURE_HOME})"
                        curl -sSL -o /tmp/allure.tgz \\
                            https://github.com/allure-framework/allure2/releases/download/2.30.0/allure-2.30.0.tgz
                        tar -xzf /tmp/allure.tgz -C "$(dirname ${ALLURE_HOME})"
                    fi
                    "${ALLURE_HOME}/bin/allure" --version
                '''
            }
        }

        stage('运行测试') {
            steps {
                // 测试失败不阻断后续报告发布，仅把构建标记为 FAILURE
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh '''
                        . venv/bin/activate
                        rm -rf ./allure-results
                        PYTHONPATH=$PYTHONPATH:. pytest testcases/test_visits testcases/test_time_analysis \\
                            --alluredir=./allure-results -v
                    '''
                }
            }
        }

        stage('生成 Allure 报告 (Jenkins 内嵌)') {
            steps {
                script {
                    allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                }
            }
        }

        stage('发布报告到 GitHub Pages') {
            steps {
                // 需要在 Jenkins 中先配置一个 Username/Password 类型凭证，ID 为 github-pat-xiaobei
                // Username = GitHub 用户名（jinbanzhuan），Password = fine-grained PAT（xiaobei 仓库 Contents:R/W）
                withCredentials([usernamePassword(
                    credentialsId: 'github-pat-xiaobei',
                    usernameVariable: 'GH_USER',
                    passwordVariable: 'GH_TOKEN'
                )]) {
                    sh '''
                        set -e

                        # 1. 拉取现有 gh-pages 分支（用于保留 history/ 趋势数据）
                        rm -rf gh-pages-tmp
                        git clone --depth 1 --branch gh-pages \\
                            "https://${GH_USER}:${GH_TOKEN}@github.com/jinbanzhuan/xiaobei.git" \\
                            gh-pages-tmp
                        if [ -d gh-pages-tmp/history ]; then
                            mkdir -p allure-results/history
                            cp -r gh-pages-tmp/history/. allure-results/history/
                        fi

                        # 2. 用 allure CLI 生成完整 HTML 报告（含历史趋势）
                        rm -rf allure-report
                        "${ALLURE_HOME}/bin/allure" generate ./allure-results --clean -o allure-report

                        # 3. 清空 gh-pages 分支工作区并用新报告替换
                        cd gh-pages-tmp
                        git rm -rf . >/dev/null 2>&1 || true
                        cp -R ../allure-report/. .
                        touch .nojekyll  # 让 GitHub Pages 不走 Jekyll，避免 _ 开头目录被过滤

                        # 4. 提交并推送
                        git -c user.name="Jenkins CI" \\
                            -c user.email="jenkins@xiaobei.local" \\
                            add -A
                        git -c user.name="Jenkins CI" \\
                            -c user.email="jenkins@xiaobei.local" \\
                            commit -m "chore(pages): update Allure report from build #${BUILD_NUMBER}" \\
                            || echo "no changes to commit"
                        git push origin gh-pages
                    '''
                }
            }
        }
    }

    post {
        success {
            script {
                echo "✅测试通过！报告地址: ${env.PAGES_URL}"
                sh """
                    . venv/bin/activate
                    python utils/send_feishu.py \\
                        "https://open.feishu.cn/open-apis/bot/v2/hook/e44589a8-9547-4710-97ee-d46246466160" \\
                        "SUCCESS" \\
                        "${env.JOB_NAME}" \\
                        "${env.BUILD_NUMBER}" \\
                        "${env.BUILD_URL}" \\
                        "${env.PAGES_URL}"
                """
            }
        }
        failure {
            script {
                echo "❌ 测试失败！请查看报告: ${env.PAGES_URL} 或日志: ${env.BUILD_URL}console"
                sh """
                    . venv/bin/activate
                    python utils/send_feishu.py \\
                        "https://open.feishu.cn/open-apis/bot/v2/hook/e44589a8-9547-4710-97ee-d46246466160" \\
                        "FAILURE" \\
                        "${env.JOB_NAME}" \\
                        "${env.BUILD_NUMBER}" \\
                        "${env.BUILD_URL}" \\
                        "${env.PAGES_URL}"
                """
            }
        }
        always {
            // 清理临时目录
            sh 'rm -rf gh-pages-tmp || true'
        }
    }
}
