// Helper function gets element width
function getInnerWidth(elem) {
    return parseFloat(window.getComputedStyle(elem).width);
}

//Variable to check if the sidebar was collapsed artificially 
let artificial = false

// Function to listen to the window resizing, and to collapse the sidebar if window is under certain px
// Async for the timeout promise
async function listen_resizing(){
    // Timeout to wait for page to render completely
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Event listener for page resizing so that if it gets too small the sidebar collapsing button gets artificially clicked
    addEventListener('resize', (e)=>{
        // Get the body of HTML and check the size
        const html_body = document.querySelector('body')
        
        // If less than a thousand pixels and the sidebar is not collapsed click the element
        if (getInnerWidth(html_body) < 1000) {
            // Get sidebar button first (These are both the classes that could be assigned to it, if checked it is expanded
            const checked = document.querySelector('.checked')

            if(checked){
                artificial = true
                checked.click()
            }
            
            // If not checked at this stage, the sidebar was already collapsed and does not require any action

        }else{
            if (artificial){
                const unchecked = document.querySelector('.unchecked')
                artificial = false
                unchecked.click()
            }
        }

    })


}


// Check if the page has rendered, if it hasnt, wait for it to do
if (document.readyState == 'complete'){
    // console.log('active')
    listen_resizing()

}else {
    document.onreadystatechange = function () {
        if (document.readyState === "complete") {
            // console.log('activating')
            listen_resizing()
        }
    }
}





