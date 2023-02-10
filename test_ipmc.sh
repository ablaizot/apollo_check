i=0
for ip in 192.168.22.41
do
        if ping -c 1 "${ip}" &> /home/ablaizot/pingcheck
        then
                { echo -e "info\r\n"; sleep 1; echo -e "tcnrd\r\n";sleep 1;echo -e "eepromrd\r\n";sleep 1;}| telnet "${ip}" > logs_ipmc
                        date >> logs_ipmc_${i}
                i = $((i + 1))
        else
                echo "error"
        fi
done
