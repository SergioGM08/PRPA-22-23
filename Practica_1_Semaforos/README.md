# Practica-1--Semaforos
Problema del Productor-Consumidor
Nos enfrentamos al problema del productor-consumidor.
Tenemos 5 productores, los procecsos, que generan números aleatorios positivos de manera creciente y que emiten un -1 cuando han terminado de producir. Los anteriores se almacenan en storage que está compartidocompartido, si hay hueco en este, desde el cual el consumidor coge el mínimo generado y lo añade a la lista in_order, escribiendo un -2 que indica que el espacio ocupado por dicho elemento ha quedado vacío.

El control sobre la actuación de los procesos está llevado a cabo mediante los semáforos empty y non_empty.
Se finaliza el código en la función main poniendo en funcionamiento los procesos con p.start() y haciendo que se junten en el hilo principal de ejecución con p.join() para no recibir resultados inesperados
