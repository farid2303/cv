# Bolt's Journal - Critical Learnings Only

## 2025-11-02 - Image Dimensions and Layout Shifts in Pure HTML
**Learning:** In plain HTML pages without CSS frameworks, missing image `width` and `height` attributes causes Cumulative Layout Shift (CLS) when images load asynchronously, pushing content down and triggering expensive browser reflows of parent table containers.
**Action:** Always provide explicit intrinsic dimensions (`width` and `height`) and `decoding="async"` on `<img>` tags to allocate space before the image binary is downloaded and decoded.
