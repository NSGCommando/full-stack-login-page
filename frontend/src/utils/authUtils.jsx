export const clearSessionData = () => {
    if (window.history.replaceState) {
        window.history.replaceState({}, document.title);
    }
}