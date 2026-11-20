@echo VOCE PRECISA DO XDELTA.EXE NA MESMA PASTA DO ARQUIVO A SER CORRIGIDO.
@echo *******
@echo Este patch vai SOBRE a traducao em ingles v1.10. Antes, aplique o patch em ingles.
@echo A faixa 1 em ingles deve se chamar:
@echo "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01).bin"
@echo e ter CRC 7AB83E03. Se nao tiver, aperte Ctrl-C para parar. Senao,
@pause
xdelta -d -s "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01).bin" SSRPG_PTBR_beta1.xdelta "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01)-PTBR.bin"
rename "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01).bin" "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01)-INGLES.bin"
rename "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01)-PTBR.bin" "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) (Track 01).bin"
@pause
