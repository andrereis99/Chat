# Chat

Apenas existe um requisito para entrar, a inserção de um username sem espaços e que ainda não esteja em uso. Após isto, o utilizador pode trocar de salas livremente, exceto para salas privadas onde este não seja um moderador.

Comandos
• “exit” – terminar sessão.
• “rooms” – visualizar todas as salas e utilizadores dentro delas.
• “create [nome da sala] [priv]” – criar uma sala com um nome ainda não existente, poderá
  ser uma sala privada caso o utilizador escreva “priv” no final do comando (ex.: “create
  room1 priv”). Caso escreva apenas com o formato “create [nome da sala]” a sala será
  publica (ex.: “create room1”).
• “ban [nome do utilizador] [tempo em segundos]” – banir utilizador da sala onde quem
  executou o comando se encontra, caso seja um ban temporário adiciona-se o tempo em
  segundo no final do comando (ex.: “ban user1 15”), se o comando estiver apenas com o
  formato “ban [nome do utilizador]” o ban será permanente (ex.: “ban user1”).
• “remove ban [nome do utilizador]” – remover o ban dum utilizador na sala onde quem
  executou o comando se encontra (ex.: “remove ban user1”)
• “giveMod [nome do utilizador]” – Dar permissões de moderador a um outro utilizador na
  sala onde o quem executa o comando se encontra. (ex.: “giveMod user1”)
• “remove mod [nome do utilizador]” – tirar permissões de moderador dum utilizador na sala
  onde quem executou o comando se encontra. (ex.: “remove mod user1”)
