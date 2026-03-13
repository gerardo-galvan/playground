// Store the most recently intercepted video URL
let latestReelUrl = "";

// Listen to network requests to sniff out raw MP4 files
browser.webRequest.onBeforeRequest.addListener(
  (details) => {
    // Focus specifically on mp4 files coming from Meta's CDNs
    if (details.url.includes('.mp4') && details.url.includes('fbcdn.net')) {
      try {
        let urlObj = new URL(details.url);
        
        // Strip out the chunking parameters so the CDN serves the full file
        if (urlObj.searchParams.has('bytestart')) {
          urlObj.searchParams.delete('bytestart');
          urlObj.searchParams.delete('byteend');
        }
        
        latestReelUrl = urlObj.toString();
        console.log("Sniffed and cleaned full Reel URL:", latestReelUrl);
        
      } catch (e) {
        console.error("Failed to clean URL", e);
      }
    }
  },
  { urls: ["<all_urls>"] }
);

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'download_media') {
    let finalUrl = message.url;
    let filename = '';
    
    // Grab the username from the message, or default to empty if it didn't arrive
    let userPrefix = message.username ? `${message.username}_` : 'unknown_user_';

    if (message.isReel) {
      if (!latestReelUrl) {
        console.error("No Reel URL has been sniffed yet!");
        return;
      }
      finalUrl = latestReelUrl;
      // Prepend the username to the Reel filename
      filename = `${userPrefix}reel_${Date.now()}.mp4`;
    } else {
      try {
        const urlObj = new URL(finalUrl);
        let originalName = urlObj.pathname.split('/').pop() || `media_${Date.now()}`;
        // Prepend the username to standard media
        filename = `${userPrefix}${originalName}`;
      } catch (e) {
        const extension = finalUrl.includes('video') ? 'mp4' : 'jpg';
        filename = `${userPrefix}media_${Date.now()}.${extension}`;
      }
    }
    
    browser.downloads.download({
      url: finalUrl,
      filename: `Instagram/${filename}`,
      saveAs: false 
    }).then(id => {
      console.log("Download started successfully with ID:", id);
    }).catch(err => {
      console.error("Download failed:", err);
    });
  }
});