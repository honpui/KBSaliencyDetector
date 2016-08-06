function [regions] = kbdetect(in_im, windows, mask)

from skimage import color


if in_im.ndim != 2:
    im = color.rgb2gray(in_im);
else:
    im = in_im

nr,nc = im.shape

# find pixels that we are going to examine
r,c = np.nonzero(mask)
nPix = len(r)

# get how many scales we are doing
nScales = len(windows)


QUANTIZATION = 16
edges = [_ for _ in range(0,256,QUANTIZATION)]


last_h = np.zeros((len(edges)-1,nPix))
ss_x = np.zeros((nScales, nPix))
entropy = np.zeros((nScales, nPix))

out_scales = nScales

# now iterate
for s_count in range(1,nScales):
    win_size = windows[s_count]
    this_win = int((win_size)/2);

    # if scale is too big(more than half image size), then exclude that
    if this_win+1 > nr/2 or this_win+1 > nc/2:
        out_scales = s_count-1
        break

    for i in range(1,nPix):
        # ignore points too close to the edge of the image
        if s_count == 2 and r(i) == 93 && c(i) == 93:
            dummy = 1;
        end

        min_r = r[i]-this_win
        min_c = c[i]-this_win
        max_r = min_r + win_size-1
        max_c = min_c + win_size-1

        if min_r < 1:
            min_r = 1

        if max_r > nr:
            max_r = nr

        if min_c < 1:
            min_c = 1

        if max_c > nc:
            max_c = nc

         # if (min_r < 1 || max_r > nr || min_c < 1 || max_c > nc)
         #     continue;
         # end

         # compute the histogram of intensity values in this region
        patch = im[min_r:max_r, min_c:max_c]
        

        h = np.histogram(patch,bins=edges,normed=True)
        h = h[1:-1]

        # index of histogram values greater than zero
        indexes = np.nonzero(h > 0)
        entropy[s_count,i] = -sum(h[idx].*log(h[idx]))

        if s_count >= 2:
            dif = abs(h-last_h[:,i])
            factor = windows[s_count]^2/(2*windows[s_count]-1)
            factor1 = (windows[s_count]+1)^2/(2*windows[s_count]+1)
            ss_x[s_count,i] = factor * sum(dif);
            ss_x_new[s_count,i] = factor1*sum(dif);

            if s_count == 2:
                ss_x[s_count-1,i] = ss_x[s_count,i]
                #  New modification - it can also be zero as it is not going to matter
                ss_x_new[s_count-1,i] = ss_x_new[s_count,i] 

        last_h(:,i) = h;


# now find local maxima in scale space by looking at the second derivative
# being less than zero. calculate the weights and smooth since the first
# derivative calculation will be noisy

fxx = np.transpose([1 -2 1])

weight = ss_x[1:out_scales,:]
# weight1 = ss_x_new(1:out_scales,:);
# # New modification - change the weight 
# temp=weight1(:,2:end)
# temp(:,end+1)=zeros(size(temp,1),1)
# new_weight = (weight+temp)/2
# new_weight(:,end)=new_weight(:,end-1)


ss_xx = imfilter(entropy(1:out_scales,:), fxx, 'replicate')
ss_xx[1,:] = 0
[int_pts] = np.nonzero(ss_xx < 0)

# weight these points by the weighting function, which is the scale window
# size times the first derivative of the scale-space function

# New modification - change 'weights' to 'new_weights'
regions.gamma = entropy[int_pts] .* weight(int_pts) 
[scales,locs] = ind2sub([out_scales nPix], int_pts);

regions.scale = np.transpose(windows(scales))
regions.r = r[locs]
regions.c = c[locs]
