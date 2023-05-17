/**
 * 删除确认，需要把链接class设为delete
 */
$(document).ready(function(){
        $(".delete").click(function(event){
            if(!confirm('是否确认删除？')) {
                event.preventDefault();}
        });
    });
