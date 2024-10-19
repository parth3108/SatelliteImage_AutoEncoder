<script lang="js">
	import { Button, buttonVariants } from '$lib/components/ui/button/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as Tabs from '$lib/components/ui/tabs/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
</script>

<Dialog.Root>
	<Dialog.Trigger class={buttonVariants({ variant: 'outline' })}
		>How to Interpret Results</Dialog.Trigger
	>
	<Dialog.Content class="flex max-h-[90vh] max-w-[900px] flex-col items-start">
		<Dialog.Header>
			<Dialog.Title>Metrics</Dialog.Title>
			<Dialog.Description>How to Interpret Results</Dialog.Description>
		</Dialog.Header>
		<div class="flex h-full w-full flex-col">
			<Tabs.Root value="psnr" class="w-full">
				<Tabs.List class="grid w-full grid-cols-4">
					<Tabs.Trigger value="psnr">PSNR</Tabs.Trigger>
					<Tabs.Trigger value="ssim">SSIM</Tabs.Trigger>
					<Tabs.Trigger value="mse">MSE</Tabs.Trigger>
					<Tabs.Trigger value="lpips">LPIPS</Tabs.Trigger>
				</Tabs.List>
				<Tabs.Content value="psnr">
					<Card.Root class="flex max-h-[72vh] min-h-[72vh] flex-grow overflow-y-auto text-justify">
						<Card.Content class="space-y-2">
							<span class="font-bold"> Description </span>
							<br />
							<p>
								PSNR is a metric used to measure the quality of reconstructed images compared to
								original images, particularly in image compression and video encoding applications.
								It is defined as the ratio between the maximum possible power of a signal (the
								original image) and the power of corrupting noise (the difference between the
								original and reconstructed images).
							</p>
							<br />

							<span class="font-bold"> PSNR Formula </span>
							<br />
							<p>PSNR = 10 * log10(MAX_I^2 / MSE)</p>
							<br />
							<span class="font-bold"> Calculation </span>
							<ul class="list-disc pl-5">
								<li>MAX_I: Maximum possible pixel value of the image (255 for 8-bit images).</li>
								<li>MSE: Mean Squared Error calculated as: MSE = (1/N) * sum((I(i) - K(i))^2)</li>
								<ul class="list-disc pl-10">
									<li>I: Original image.</li>
									<li>K: Reconstructed image.</li>
									<li>N: Number of pixels in the image.</li>
								</ul>
							</ul>
							<br />
							<span class="font-bold"> Interpreting PSNR Values </span>
							<ul class="list-disc pl-5">
								<li>Higher values indicate better quality.</li>
								<li>Common thresholds</li>
								<ul class="list-disc pl-10">
									<li>Below 20 dB: Poor quality; noticeable distortion.</li>
									<li>20-30 dB: Fair to good quality; noticeable artifacts may be present.</li>
									<li>30-40 dB: Good quality; generally acceptable for most applications.</li>
									<li>
										Above 40 dB: Excellent quality; often indistinguishable from the original image.
									</li>
								</ul>
							</ul>
							<br />
							<span class="font-bold"> Limitations </span>
							<ul class="list-disc pb-4 pl-5">
								<li>PSNR may not correlate well with perceived visual quality.</li>
								<li>
									It does not account for how humans perceive images; two images with the same PSNR
									might look different to the human eye.
								</li>
							</ul>
						</Card.Content>
					</Card.Root>
				</Tabs.Content>
				<Tabs.Content value="ssim">
					<Card.Root class="flex max-h-[72vh] min-h-[72vh] flex-grow overflow-y-auto text-justify">
						<Card.Content class="space-y-2">
							<span class="font-bold"> Description </span>
							<br />
							<p>
								SSIM is a perceptual metric that quantifies the similarity between two images. It is
								based on the idea that the human visual system is highly sensitive to structural
								information in an image. SSIM considers changes in structural information,
								luminance, and contrast, providing a more accurate measure of perceived image
								quality than metrics like PSNR.
							</p>
							<br />
							<span class="font-bold"> SSIM Formula </span>
							<br />
							<p>
								SSIM(x, y) = (2 * μ_x * μ_y + C1) * (2 * σ_xy + C2) / ((μ_x^2 + μ_y^2 + C1) * (σ_x^2
								+ σ_y^2 + C2))
							</p>
							<br />
							<span class="font-bold"> Calculation </span>
							<ul class="list-disc pl-5">
								<li>μ_x and μ_y: Mean values of the two images.</li>
								<li>σ_x^2 and σ_y^2: Variances of the two images.</li>
								<li>σ_xy: Covariance between the two images.</li>
								<li>
									C1 and C2: Constants to stabilize the division; typically C1 = (K1 * L)^2 and C2 =
									(K2 * L)^2, where K1 and K2 are small constants, and L is the dynamic range of the
									pixel values.
								</li>
							</ul>
							<br />
							<span class="font-bold"> Interpreting SSIM Values </span>
							<ul class="list-disc pl-5">
								<li>SSIM values range from -1 to 1.</li>
								<li>A value of 1 indicates perfect structural similarity.</li>
								<li>
									Values closer to 1 indicate higher similarity, while values closer to -1 indicate
									lower similarity.
								</li>
							</ul>
							<br />
							<span class="font-bold"> Typical ranges </span>
							<ul class="list-disc pl-5">
								<li>0.9 to 1.0: Excellent quality; very similar images.</li>
								<li>0.7 to 0.9: Good quality; noticeable but acceptable differences.</li>
								<li>0.5 to 0.7: Fair quality; significant differences.</li>
								<li>Below 0.5: Poor quality; very different images.</li>
							</ul>
							<br />
							<span class="font-bold"> Limitations </span>
							<ul class="list-disc pb-4 pl-5">
								<li>
									SSIM can be sensitive to alignment; images must be properly aligned to obtain
									accurate results.
								</li>
								<li>
									It may not capture all perceptual differences, especially for images with
									significant variations in lighting or content.
								</li>
							</ul>
						</Card.Content>
					</Card.Root>
				</Tabs.Content>
				<Tabs.Content value="mse">
					<Card.Root class="flex max-h-[72vh] min-h-[72vh] flex-grow overflow-y-auto text-justify">
						<Card.Content class="space-y-2">
							<span class="font-bold"> Description </span>
							<br />
							<p>
								MSE is a measure of the average squared differences between the original and
								reconstructed images. It quantifies the error introduced by the compression or
								reconstruction process, providing a numerical value that indicates how closely the
								two images match.
							</p>
							<br />
							<span class="font-bold"> MSE Formula </span>
							<br />
							<p>MSE = (1/N) * sum((I(i) - K(i))^2)</p>
							<br />
							<span class="font-bold"> Calculation </span>
							<ul class="list-disc pl-5">
								<li>I(i): Pixel value of the original image at position i.</li>
								<li>K(i): Pixel value of the reconstructed/compressed image at position i.</li>
								<li>N: Total number of pixels in the image.</li>
							</ul>
							<br />
							<span class="font-bold"> Interpreting MSE Values </span>
							<ul class="list-disc pl-5">
								<li>
									Lower MSE values indicate better quality, as they represent less deviation from
									the original image.
								</li>
								<li>
									An MSE of 0 indicates perfect reconstruction, meaning the two images are
									identical.
								</li>
								<li>Common interpretation ranges:</li>
								<ul class="list-disc pl-10">
									<li>0 to 10: Excellent quality; minimal differences.</li>
									<li>10 to 20: Good quality; slight differences may be noticeable.</li>
									<li>20 to 30: Fair quality; noticeable differences.</li>
									<li>Above 30: Poor quality; significant differences.</li>
								</ul>
							</ul>
							<br />
							<span class="font-bold"> Limitations </span>
							<ul class="list-disc pb-4 pl-5">
								<li>
									MSE does not account for perceptual differences; it treats all pixel differences
									equally, which may not align with human visual perception.
								</li>
								<li>It can be overly sensitive to noise and outliers.</li>
							</ul>
						</Card.Content>
					</Card.Root>
				</Tabs.Content>
				<Tabs.Content value="lpips">
					<Card.Root class="flex max-h-[72vh] min-h-[72vh] flex-grow overflow-y-auto text-justify">
						<Card.Content class="space-y-2">
							<span class="font-bold"> Description </span>
							<br />
							<p>
								LPIPS is a perceptual metric designed to measure the similarity between two images
								based on deep learning features rather than pixel-wise differences. It captures
								perceptual differences more effectively than traditional metrics like PSNR or MSE,
								as it considers the way humans perceive visual content.
							</p>
							<br />
							<span class="font-bold"> LPIPS Metrics </span>
							<br />
							<p>
								LPIPS compares the feature representations of two images as extracted from a
								pretrained convolutional neural network (CNN). The differences in these features are
								aggregated to provide a single score that reflects perceptual similarity.
							</p>
							<br />
							<span class="font-bold"> Interpreting LPIPS Values </span>
							<ul class="list-disc pl-5">
								<li>LPIPS values typically range from 0 to 1.</li>
								<li>
									A value of <b>0</b> indicates that the two images are perceptually identical.
								</li>
								<li>Higher values indicate greater perceptual dissimilarity.</li>
								<li>Common interpretation ranges:</li>
								<ul class="list-disc pl-10">
									<li>0 to 0.1: Excellent similarity; nearly indistinguishable images.</li>
									<li>0.1 to 0.3: Good similarity; minor perceptual differences.</li>
									<li>0.3 to 0.5: Moderate similarity; noticeable differences.</li>
									<li>Above 0.5: Poor similarity; significant perceptual differences.</li>
								</ul>
							</ul>
							<br />
							<span class="font-bold"> Advantages </span>
							<ul class="list-disc pb-4 pl-5">
								<li>
									LPIPS is designed to align better with human perception than pixel-wise metrics.
								</li>
								<li>
									It captures perceptual nuances and can effectively evaluate image quality in
									various applications, such as image compression, style transfer, and
									super-resolution.
								</li>
							</ul>
							<br />
							<span class="font-bold"> Limitations </span>
							<ul class="list-disc pb-4 pl-5">
								<li>
									LPIPS requires a pretrained model and may involve additional computational
									overhead.
								</li>
								<li>
									The interpretation of LPIPS values can depend on the context and specific use
									case.
								</li>
							</ul>
						</Card.Content>
					</Card.Root>
				</Tabs.Content>
			</Tabs.Root>
		</div>
	</Dialog.Content>
</Dialog.Root>
