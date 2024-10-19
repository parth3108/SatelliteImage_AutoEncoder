<script>
	import { Presentation } from 'lucide-svelte';
</script>

<div class="flex h-full flex-col">
	<span class="flex max-h-14 min-h-14 flex-row items-center gap-4 border-b pl-4 pr-8">
		<Presentation size="24" />
		<div class="flex flex-row items-center gap-4">Presentation</div>
	</span>
	<div class="m-4 h-full rounded-lg border">
		<iframe
			style="border: 1px solid rgba(0, 0, 0, 0.1);"
			width="100%"
			height="100%"
			src="https://embed.figma.com/slides/oiylEanIde3RKnD1cTKOxC/SatEval?node-id=1-25&embed-host=share"
			allowfullscreen
			title="Presentation"
		></iframe>
	</div>
</div>
