/* DOS CP850 mapping; browser TextDecoder does not implement this encoding. */
(() => {
  'use strict';
  const high = 'ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑªº¿®¬½¼¡«»░▒▓│┤ÁÂÀ©╣║╗╝¢¥┐└┴┬├─┼ãÃ╚╔╩╦╠═╬¤ðÐÊËÈıÍÎÏ┘┌█▄¦Ì▀ÓßÔÒõÕµþÞÚÛÙýÝ¯´\xad±‗¾¶§÷¸°¨·¹³²■\xa0';
  function cp850(bytes) {
    return Array.from(bytes, b => b < 128 ? String.fromCharCode(b) : high[b - 128]).join('');
  }
  function penalty(text) {
    return (text.match(/[\uFFFD\u0080-\u009f]/g) || []).length * 10 +
      (text.match(/[\u2500-\u259f]/g) || []).length * 3 +
      (text.match(/m[ýü](?=\s)|[a-zA-Z][„”†‡‰][a-zA-Z]/g) || []).length * 6;
  }
  window.KPGaebEncoding = {
    decode(buffer, preferred = 'auto') {
      const bytes = new Uint8Array(buffer);
      if (preferred === 'cp850') return cp850(bytes);
      if (preferred !== 'auto') return new TextDecoder(preferred).decode(bytes);
      try { return new TextDecoder('utf-8', {fatal:true}).decode(bytes); } catch (_) {}
      const windows = new TextDecoder('windows-1252').decode(bytes);
      const dos = cp850(bytes);
      return penalty(dos) < penalty(windows) ? dos : windows;
    }
  };
})();
