health_check_responses = {
    200: {
        "description": "A aplicação e suas dependências estão saudáveis e prontas para receber tráfego.",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Status geral da aplicação. Será 'ok' neste caso de status 200.",
                            "example": "ok"
                        },
                        "checks": {
                            "type": "object",
                            "description": "Objeto contendo os resultados das verificações de cada dependência.",
                            "properties": {
                                "banco_de_dados": {
                                    "type": "object",
                                    "description": "Resultado da verificação do banco de dados.",
                                    "properties": {
                                        "status": {
                                            "description": "Status da conexão com o banco de dados.",
                                            "example": "ok"
                                        },
                                        "latency_ms": {
                                            "type": "number",
                                            "format": "float",
                                            "description": "Tempo de resposta da consulta de verificação em milissegundos.",
                                            "example": 27.03
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    503: {
        "description": "A aplicação está em execução, mas alguma de suas dependências críticas não está saudável. O serviço está temporariamente indisponível.",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Status geral da aplicação. Será 'error' neste caso de status 503.",
                            "example": "error"
                        },
                        "checks": {
                            "type": "object",
                            "description": "Objeto contendo os resultados das verificações de cada dependência.",
                            "properties": {
                                "banco_de_dados": {
                                    "type": "object",
                                    "description": "Resultado da verificação do banco de dados.",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "description": "Status da conexão com o banco de dados.",
                                            "example": "error"
                                        },
                                        "latency_ms": {
                                            "type": "number",
                                            "format": "float",
                                            "description": "Tempo de resposta da consulta de verificação em milissegundos.",
                                            "example": 2104.55
                                        },
                                        "detail": {
                                            "type": "string",
                                            "description": "Detalhes do erro que ocorreu durante a verificação.",
                                            "example": "connection to db server failed: Connection refused"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}