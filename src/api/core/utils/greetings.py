import random

greetings = [
  "Hola, soy su asistente legal virtual. Estoy aquí para ayudarle con consultas jurídicas, documentación y orientación en asuntos legales. ¿En qué puedo asistirle hoy?",
  "Buenos días/tardes. Soy su asistente legal especializado en derecho civil, mercantil y laboral. ¿Sobre qué aspecto legal necesita asesoramiento?",
  "Bienvenido/a al servicio de asistencia legal virtual. Puedo ayudarle con consultas, redacción de documentos y orientación jurídica general. ¿Cuál es su consulta?",
  "Hola, soy su consultor jurídico digital. Estoy capacitado para asistirle en materias legales, revisión de contratos y asesoramiento normativo. ¿En qué puedo servirle?",
  "Buen día. Como asistente legal, puedo brindarle orientación en derechos y obligaciones, procedimientos judiciales y documentación legal. ¿Qué requiere hoy?",
  "Saludos. Soy su asistente en asuntos legales, especializado en derecho mexicano. Puedo ayudarle con consultas, formatos y trámites jurídicos. ¿Cómo puedo apoyarle?",
  "Hola, bienvenido/a al sistema de asesoría legal. Estoy aquí para resolver sus dudas jurídicas, explicar conceptos legales y asistirle en procedimientos. ¿Cuál es su situación?",
  "Buenos días. Como asistente jurídico virtual, puedo orientarle en contratos, demandas, recursos legales y cumplimiento normativo. ¿Sobre qué tema desea consultar?",
  "Hola, soy su asistente para temas legales. Ofrezco asesoría en derecho civil, mercantil, laboral y administrativo. ¿En qué área necesita ayuda específicamente?",
  "Bienvenido/a al servicio de consultoría legal. Estoy preparado para asistirle con análisis de casos, revisión documental y orientación procesal. ¿Cómo puedo ayudarle hoy?"
]

def get_greeting():
    random_index = random.randint(0, len(greetings) - 1)
    random_greeting = greetings[random_index]

    return random_greeting

