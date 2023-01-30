pipeline {
    agent any
    parameters {
        string(name: 'TENANT_NAME', defaultValue: 'myTenant')
        string(name: 'APP_PROFILE_NAME', defaultValue: 'myAppProfile')
        string(name: 'EPG_NAME', defaultValue: 'myEPG')
    }
    stages {
        stage('Retrieve Credentials') {
            steps {
                withCredentials([thycotic(credentialsId: 'your_credentials_id')]) {
                    script {
                        env.APIC_IP = thycotic_secret['APIC IP']
                        env.USERNAME = thycotic_secret['username']
                        env.PASSWORD = thycotic_secret['password']
                    }
                }
            }
        }
        stage('Run Script') {
            steps {
                script {
                    sh '''
                        python aci_script.py --tenant_name $TENANT_NAME --app_profile_name $APP_PROFILE_NAME --epg_name $EPG_NAME --apic_ip $APIC_IP --username $USERNAME --password $PASSWORD
                    '''
                }
            }
        }
    }
}