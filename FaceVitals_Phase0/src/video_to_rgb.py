#!/usr/bin/env python3
"""Minimal real-video ROI RGB extractor; proof-of-concept ONLY.

Uses OpenCV Haar face detection and approximate rectangular facial patches;
NOT a validated face mesh, skin segmentation, stable identity tracker or rPPG pipeline.

python src/video_to_rgb.py --video licensed_face_video.mp4 --out results/roi_trace.csv

Select a clip with one unobstructed face and stable fps. Keeps missing detections
as NaN, NEVER silently fabricates colors, so the HR estimator will reject those
until proper tracking/gap handling is implemented. Does not collect consent.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import cv2


def intersection_over_union(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    x0, y0 = max(ax,bx), max(ay,by)
    x1, y1 = min(ax+aw,bx+bw), min(ay+ah,by+bh)
    area = max(0,x1-x0)*max(0,y1-y0)
    return area/max(1, aw*ah+bw*bh-area)


def roi_patch(box, region: str):
    x,y,w,h=box
    # Locations relative to a generic face bounding rectangle; NOT landmarks.
    frac = {
        "forehead": (.27, .12, .73, .30),
        "left_cheek": (.12, .48, .43, .72),
        "right_cheek": (.57, .48, .88, .72),
    }[region]
    return tuple(map(int, (x + frac[0]*w, y + frac[1]*h,
                           x + frac[2]*w, y + frac[3]*h)))


def crop_average_rgb(img_rgb, rect):
    x0,y0,x1,y1=rect
    h,w=img_rgb.shape[:2]
    x0,x1=max(0,x0),min(w,x1)
    y0,y1=max(0,y0),min(h,y1)
    if x1-x0<8 or y1-y0<8:
        return np.array([np.nan]*3)
    px=img_rgb[y0:y1,x0:x1].reshape(-1,3).astype(np.float64)/255.0
    # Ignore clipped bright/dark pixels; no skin-tone threshold applied.
    keep=np.logical_and(np.max(px,axis=1)<0.985, np.max(px,axis=1)>0.02)
    if np.sum(keep)<40:
        return np.array([np.nan]*3)
    return np.mean(px[keep],axis=0)


def convert(video: Path, output: Path, every_n_frames=1):
    video=Path(video); output=Path(output)
    if not video.exists(): raise FileNotFoundError(video)
    classifier=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    if classifier.empty(): raise RuntimeError('OpenCV face detector unavailable')
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise RuntimeError(f'Could not decode {video}')
    fps=float(cap.get(cv2.CAP_PROP_FPS))
    if not np.isfinite(fps) or fps<=0: raise RuntimeError('Unknown or zero video fps')
    prev_box=None
    rows=[]
    idx=0
    while True:
        ok, bgr=cap.read()
        if not ok: break
        if idx%every_n_frames!=0:
            idx+=1;continue
        rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
        candidates=classifier.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60,60))
        candidates=[tuple(int(z) for z in b) for b in candidates]
        if candidates:
            if prev_box is None:
                target=max(candidates,key=lambda b:b[2]*b[3])
            else:
                target=max(candidates,key=lambda b:intersection_over_union(b,prev_box))
                # IoU of 0 indicates an unsafe jump; reject rather than switch identity.
                if intersection_over_union(target,prev_box)<=0:
                    target=None
        else: target=None
        if target is not None:
            prev_box=target
            patches=[crop_average_rgb(rgb,roi_patch(target,s))
                     for s in ('forehead','left_cheek','right_cheek')]
            patches=np.array(patches)
            if np.all(np.isfinite(patches)):
                # Equal region weighting, not pixel weighting: avoids cheek area dominating.
                avg=np.mean(patches,axis=0)
            else:
                avg=np.array([np.nan]*3)
        else:
            patches=np.full((3,3),np.nan)
            avg=np.array([np.nan]*3)
        # Decode timestamps may vary. FPS-derived time is fallback only.
        decoder_ms=float(cap.get(cv2.CAP_PROP_POS_MSEC))
        timestamp=(decoder_ms/1000 if decoder_ms>0 else idx/fps)
        row={"timestamp_s":timestamp,"frame_index":idx,"detected":bool(target is not None),
             "n_faces_detected":len(candidates),"r":avg[0],"g":avg[1],"b":avg[2]}
        for region,patch in zip(('forehead','left_cheek','right_cheek'),patches):
            for cname,v in zip(('r','g','b'),patch):row[f'{region}_{cname}']=v
        rows.append(row)
        idx+=1
    cap.release()
    if not rows: raise RuntimeError('Video contains no decodable frames')
    df=pd.DataFrame(rows)
    output.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(output,index=False)
    missing=int(df[['r','g','b']].isna().any(axis=1).sum())
    meta={"video_input":str(video),"output_csv":str(output),"fps_declared":fps,
          "frames_total":idx,"frames_kept":len(df),"frames_missing_roi":missing,
          "missing_fraction":missing/len(df),"detector":"OpenCV Haar frontalface_default",
          "tracking":"consecutive IoU only; initial largest face; not validated multi-person tracking",
          "skin_roi":"approximate geometric forehead/cheek rectangles, not skin segmentation",
          "reference_hr":"not available in this conversion",
          "clinical_validation":False}
    output.with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    if missing:
        print(f'WARNING: {missing}/{len(df)} samples have missing ROI. No imputation performed; do not pass to HR estimator without a documented missing-data protocol.')
    print(f'Wrote {len(df)} RGB observations to {output}; fps={fps:.2f}, NaN frames={missing}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--every-n-frames',type=int,default=1)
    args=parser.parse_args()
    if args.every_n_frames<1:parser.error('--every-n-frames must be >=1')
    convert(args.video,args.out,args.every_n_frames)

if __name__=='__main__':main()
