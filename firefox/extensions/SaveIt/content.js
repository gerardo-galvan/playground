async function blobToBase64(blobUrl) {
  try {
    // Fetch the data from the blob URL
    const response = await fetch(blobUrl);
    const blob = await response.blob();
    
    // Convert it to a Base64 string using FileReader
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error("Failed to convert blob:", error);
    return null;
  }
}


function addDownloadButtons() {
  // Selects images and videos. You might need to tweak this selector based on the exact website's DOM structure.
  const mediaElements = document.querySelectorAll('img, video');

  mediaElements.forEach(media => {
    // Prevent attaching multiple buttons to the same image/video
    if (media.dataset.innertelProcessed) return;
    media.dataset.innertelProcessed = "true";

    // Create the button
    const btn = document.createElement('button');
    btn.className = 'download-btn';
    btn.innerText = '⬇ Save';
    btn.title = "Download to local folder";

    // Create a wrapper to float the button over the media
    const btnWrapper = document.createElement('div');
    btnWrapper.style.position = 'absolute';
    btnWrapper.style.top = '10px';
    btnWrapper.style.right = '10px';
    btnWrapper.style.zIndex = '9999';
    btnWrapper.appendChild(btn);

    // Attach to the parent container safely without breaking site layouts
    const parent = media.parentElement;
    if(parent) {
      if(window.getComputedStyle(parent).position === 'static') {
        parent.style.position = 'relative';
      }
      parent.appendChild(btnWrapper);
    }
 
    // Handle the click
    btn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation(); 
      
      let src = media.src;
      if (!src && media.tagName === 'VIDEO') {
        const source = media.querySelector('source');
        if (source) src = source.src;
      }
      
      if (src) {
        // --- USERNAME SCRAPING LOGIC ---
        let scrapedUsername = "unknown_user";
        
        // 1. Traverse up the DOM to find the main container for this specific post
        // Instagram usually wraps individual feed posts or modal popups in an <article> tag
        const postContainer = media.closest('article') || document.body;
        
        // 2. Look for the username link (usually the first link in the post header)
        // We look for an <a> tag that has text but doesn't contain an image (to avoid profile pics)
        const allLinks = postContainer.querySelectorAll('header a, a');
        for (let link of allLinks) {
          const text = link.innerText.trim();
          // If it has text, doesn't have spaces (usernames usually don't), and isn't a generic word
          if (text && !text.includes('\n') && !text.includes(' ') && text !== 'Follow') {
            scrapedUsername = text;
            break;
          }
        }
        
        // 3. Clean the username just in case it picked up weird characters
        scrapedUsername = scrapedUsername.replace(/[^a-zA-Z0-9_.]/g, '');
        if (!scrapedUsername) scrapedUsername = "unknown_user";
        // ------------------------------------

        const originalText = btn.innerText;
        btn.innerText = '⏳ Processing...';

        if (src.startsWith('blob:') && media.tagName === 'VIDEO') {
          browser.runtime.sendMessage({ 
            action: 'download_media', 
            isReel: true,
            username: scrapedUsername // Send the username to the background script
          });
        } else {
          browser.runtime.sendMessage({ 
            action: 'download_media', 
            url: src,
            isReel: false,
            username: scrapedUsername // Send the username to the background script
          });
        }
        
        setTimeout(() => { btn.innerText = '✔ Saved!'; }, 500);
        setTimeout(() => { btn.innerText = originalText; }, 2000);

      } else {
        alert("Sorry, couldn't find a valid source URL for this media.");
      }
    };
  });
}

// Run once on load
addDownloadButtons();

// Set up an observer to catch newly loaded images/reels as you scroll
const observer = new MutationObserver(() => {
  addDownloadButtons();
});
observer.observe(document.body, { childList: true, subtree: true });