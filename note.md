

```javascript
javascript:(function(){'use strict';function checkAndClick(){var continueButton=document.querySelector('.yx--alarm-clock');if(continueButton){continueButton.click();console.log('已自动点击继续计时按钮');}}setInterval(checkAndClick,60000);})();
```
