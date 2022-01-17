```plantuml
@startuml
skinparam componentStyle uml2
skinparam sequenceArrowThickness 2
skinparam roundcorner 5
skinparam maxmessagesize 120
skinparam sequenceParticipant underline
hide footbox
skinparam BoxPadding 2

box "Billing" #LightYellow
    actor Client
    collections nginx_billing
    collections billing
    database PostgresBilling
end box

box "Transport" #LightGray
    control Kafka
end box

box "Auth" #LightBlue
    collections auth
    database PostgresAuth
end box

box "Notifications" #Orange
    collections notifications
    control Redis
end box

Client -> nginx_billing: Proxy request
activate nginx_billing
nginx_billing -> billing: Create subscription
activate billing
billing -> PostgresBilling: Save subscription
deactivate PostgresBilling
activate Kafka
billing -> Kafka: Emit event `USER_SUBSCRIBED`
deactivate Kafka
billing -> nginx_billing: 200 OK
deactivate billing
nginx_billing -> Client: Successfully subscribed
deactivate nginx_billing

activate Kafka
activate auth
activate notifications
Kafka -> auth
activate PostgresAuth
auth -> PostgresAuth: Update User subscription info
deactivate PostgresAuth
deactivate auth

Kafka -> notifications
activate Redis
notifications -> Redis: Schedule task send_email `Information about current subscription`
deactivate Redis
deactivate notifications
deactivate Kafka
@enduml
```