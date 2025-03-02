**CumpleBot** es un bot para Telegram que avisa los cumpleaños de una lista

Es mi primer Proyecto de vibe coding, usando Claude Sonnet 3.7 y Grok3. Lo instalé en un raspberry pi que tengo conectado a mi impresora 3D, pero puede andar en cualquier Linux que tengan online, los requerimientos son mínimos.

El bot tiene commandos que son auto explicativos, una vez creado el bot via Telegram BotFather, pueden cargarlos en editar commandos del bot también en BotFather:

```plaintext
lista - Muestra la lista de cumpleaños
modificar - Modifica o crea una entrada de cumpleaños. Formato Nombre Completo,dia,mes,año
cumple - Informa si hoy hay cumpleaños
proximo - Muestra el próximo cumpleaños
ayuda - Muestra la lista de comandos disponibles
```

La unica opción que no está listada ahi es por si un usuario de la lista se muere y se lo quiere recordar todos los años, el formato para actualizar seria: 

```plaintext
/modificar Pirulo Test QEPD,1,1,1967
```

(si no se sabes el año poné 1900 al crear la lista de cumpleaños) Si el sicario reporto erróneamente la muerte :) agregando un guion después de QEPD le saca esa etiqueta

```plaintext
/modificar Pirulo Test QEPD-,1,1,1967
```

No se pueden borrar contactos via comandos, me parecio una medida de seguridad simple y basica, ya que quien administra la instalacion del bot lo puede hacer facilmente desde consola

**Para instalar en tu Linux**

crea una carpeta JosBot (yo la cree en: /home/pablopeu/JosBot/) y copia los archivos ahi

a JosBot.py darle atributos 755

```plaintext
chmod 755 JosBot.py
```

El programa lo corro como un servicio, para eso hacer esto:

```plaintext
sudo nano /etc/systemd/system/josbot.service
```

y poner lo siguiente:

```plaintext
[Unit]
Description=JosBot Service
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pablopeu/JosBot/JosBot.py (modificar con las rutas correctas a tu instalacion)
WorkingDirectory=/home/pablopeu/JosBot (modificar con las ruta correcta a tu instalacion)
User=pablopeu (modificar con el nombre de usuario)
Restart=on-failure
[Install]
WantedBy=multi-user.target
```

Una vez creado este archivo, ejecutar lo siguiente:

```plaintext
sudo systemctl daemon-reload
sudo systemctl enable josbot.service
sudo systemctl start josbot.service
```

y verificar que haya arrancado con:

```plaintext
sudo systemctl status josbot.service
```

ante cualquier error que haga que no arranque se puede ver en:

```plaintext
journalctl -u josbot.service -f
```

vayan al final con la hora que le dieron inicio al servicio y le preguntan a GROK o alguna IA cual es el problema y que les tire una solucion, no sean vagos y esperen que lo solucione yo...
